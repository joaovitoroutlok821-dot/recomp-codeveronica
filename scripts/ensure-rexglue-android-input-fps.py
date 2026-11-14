#!/usr/bin/env python3
"""Apply Android input classification and low-overhead Vulkan present FPS diagnostics."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: ensure-rexglue-android-input-fps.py /path/to/rexglue-sdk")

sdk = Path(sys.argv[1]).resolve()
input_file = sdk / "src/input/sdl/sdl_input_driver.cpp"
presenter_file = sdk / "src/ui/vulkan/vulkan_presenter.cpp"
render_target_cache_file = sdk / "src/graphics/vulkan/render_target_cache.cpp"
for path in (input_file, presenter_file, render_target_cache_file):
    if not path.is_file():
        raise SystemExit(f"Required ReXGlue source file not found: {path}")

input_text = input_file.read_text(encoding="utf-8")
old_synthetic = "    info.synthetic = false;"
new_synthetic = '    info.synthetic = info.name == "Resident Evil Code Veronica Touch";'
if new_synthetic not in input_text:
    if input_text.count(old_synthetic) != 1:
        raise SystemExit("Could not uniquely locate SDL gamepad synthetic-device classification")
    input_text = input_text.replace(old_synthetic, new_synthetic, 1)
    input_file.write_text(input_text, encoding="utf-8")
if new_synthetic not in input_file.read_text(encoding="utf-8"):
    raise SystemExit("Touch gamepad synthetic-device classification verification failed")

presenter = presenter_file.read_text(encoding="utf-8")

fps_export_anchor = """namespace rex {
namespace ui {
namespace vulkan {
"""
fps_export = """namespace rex {
namespace ui {
namespace vulkan {

namespace {
std::atomic<float> g_recvx_presented_fps{0.0f};
}  // namespace

extern "C" __attribute__((visibility("default"))) float ReXGlue_GetPresentedFPS() {
  return g_recvx_presented_fps.load(std::memory_order_relaxed);
}
"""
if fps_export not in presenter:
    if presenter.count(fps_export_anchor) != 1:
        raise SystemExit("Could not uniquely locate Vulkan presenter namespace")
    presenter = presenter.replace(fps_export_anchor, fps_export, 1)
for include in ("#include <chrono>", "#include <mutex>"):
    if include not in presenter:
        anchor = "#include <cmath>"
        if anchor not in presenter:
            raise SystemExit("Could not locate Vulkan presenter standard include block")
        presenter = presenter.replace(anchor, anchor + "\n" + include, 1)

old_present = """  switch (present_result) {
    case VK_SUCCESS:
      return PaintResult::kPresented;
    case VK_SUBOPTIMAL_KHR:
      return PaintResult::kPresentedSuboptimal;"""
new_present = """  switch (present_result) {
    case VK_SUCCESS:
    case VK_SUBOPTIMAL_KHR: {
      // Count successful swapchain presentations, not guest-loop iterations.
      // Emit a low-frequency diagnostic so log collection has minimal overhead.
      static std::mutex fps_mutex;
      static auto fps_window_start = std::chrono::steady_clock::now();
      static uint64_t fps_frames = 0;
      {
        std::lock_guard<std::mutex> lock(fps_mutex);
        ++fps_frames;
        const auto now = std::chrono::steady_clock::now();
        const auto elapsed_ms =
            std::chrono::duration_cast<std::chrono::milliseconds>(now - fps_window_start).count();
        if (elapsed_ms >= 2000) {
          const double fps = static_cast<double>(fps_frames) * 1000.0 /
                             static_cast<double>(elapsed_ms);
          g_recvx_presented_fps.store(static_cast<float>(fps), std::memory_order_relaxed);
          REXLOG_INFO("[RECVX-FPS] Presented FPS: {:.1f} ({} frames / {} ms)",
                      fps, fps_frames, elapsed_ms);
          fps_frames = 0;
          fps_window_start = now;
        }
      }
      return present_result == VK_SUCCESS ? PaintResult::kPresented
                                           : PaintResult::kPresentedSuboptimal;
    }"""
if new_present not in presenter:
    if presenter.count(old_present) != 1:
        raise SystemExit("Could not uniquely locate Vulkan swapchain present result switch")
    presenter = presenter.replace(old_present, new_present, 1)
    presenter_file.write_text(presenter, encoding="utf-8")
if new_present not in presenter_file.read_text(encoding="utf-8"):
    raise SystemExit("Vulkan presented-FPS instrumentation verification failed")

# Record the final render-target backend only after every capability check and
# automatic fallback has completed. This is diagnostic-only and never changes
# the renderer selection.
render_cache = render_target_cache_file.read_text(encoding="utf-8")
render_log = """  REXGPU_INFO(
      "[RECVX-VK-DIAG] final render-target path: {}; FSI supported: {}; "
      "sample interlock: {}; pixel interlock: {}; fragment stores/atomics: {}; "
      "sample-rate shading: {}; standard sample locations: {}; "
      "D24_UNORM_S8 sampled+depth attachment: {}; "
      "16-bit UINT transfer formats: {}; 32-bit UINT transfer formats: {}; "
      "bit-exact host color transfer: {}; 2x MSAA attachments: {}",
      path_ == Path::kPixelShaderInterlock ? "FSI" : "FBO",
      fsi_path_supported,
      device_properties.fragmentShaderSampleInterlock,
      device_properties.fragmentShaderPixelInterlock,
      device_properties.fragmentStoresAndAtomics,
      device_properties.sampleRateShading,
      device_properties.standardSampleLocations,
      depth_unorm24_vulkan_format_supported_,
      color_16bit_transfer_uint_formats_supported_,
      color_32bit_transfer_uint_formats_supported_,
      bit_exact_host_color_transfer_supported,
      msaa_2x_attachments_supported_);

"""
cache_anchor = "  // Descriptor set layouts.\n"
if render_log not in render_cache:
    if render_cache.count(cache_anchor) != 1:
        raise SystemExit("Could not uniquely locate final Vulkan render-target path insertion point")
    render_cache = render_cache.replace(cache_anchor, render_log + cache_anchor, 1)
    render_target_cache_file.write_text(render_cache, encoding="utf-8")
if render_log not in render_target_cache_file.read_text(encoding="utf-8"):
    raise SystemExit("Vulkan final render-target diagnostics verification failed")

# Add bounded, diagnostic-only logging when multiple render targets use the
# same Xenos EDRAM base. The original target-retention behavior is unchanged.
collision_anchor = """      if (edram_bases[rt_other_index] == edram_base) {
        depth_and_color_rts_used_bits &= ~(uint32_t(1) << rt_other_index);
      }"""
collision_replacement = """      if (edram_bases[rt_other_index] == edram_base) {
        // Log only the first 32 collisions to keep device logs bounded.
        static uint32_t recvx_edram_collision_log_count = 0;
        if (recvx_edram_collision_log_count < 32) {
          REXGPU_INFO(
              "[RECVX-EDRAM-COLLISION] keep_rt={} drop_rt={} base={} "
              "keep_format={} drop_format={} keep_64bpp={} drop_64bpp={} "
              "interlock_barrier_only={}",
              rt_index, rt_other_index, edram_base,
              resource_formats[rt_index], resource_formats[rt_other_index],
              (rts_are_64bpp & (uint32_t(1) << rt_index)) != 0,
              (rts_are_64bpp & (uint32_t(1) << rt_other_index)) != 0,
              interlock_barrier_only);
          ++recvx_edram_collision_log_count;
        }
        depth_and_color_rts_used_bits &= ~(uint32_t(1) << rt_other_index);
      }"""
pipeline_render_cache = pipeline_render_target_cache_file.read_text(encoding="utf-8")
if collision_replacement not in pipeline_render_cache:
    if pipeline_render_cache.count(collision_anchor) != 1:
        raise SystemExit("Could not uniquely locate Xenos EDRAM duplicate-target elimination in pipeline cache")
    pipeline_render_cache = pipeline_render_cache.replace(collision_anchor, collision_replacement, 1)
    pipeline_render_target_cache_file.write_text(pipeline_render_cache, encoding="utf-8")
if collision_replacement not in pipeline_render_target_cache_file.read_text(encoding="utf-8"):
    raise SystemExit("Xenos EDRAM collision diagnostics verification failed")

print("[recvx-android-input-fps] touch gamepad is routed as a synthetic user-0 device")
print("[recvx-android-input-fps] successful Vulkan presentations are sampled every 2 seconds and exported for the overlay")
print("[recvx-android-input-fps] final Vulkan render-target path and depth/format capabilities are logged")
