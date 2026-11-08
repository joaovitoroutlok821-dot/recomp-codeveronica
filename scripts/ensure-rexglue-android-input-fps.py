#!/usr/bin/env python3
"""Apply Android input classification and low-overhead Vulkan present FPS diagnostics."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: ensure-rexglue-android-input-fps.py /path/to/rexglue-sdk")

sdk = Path(sys.argv[1]).resolve()
input_file = sdk / "src/input/sdl/sdl_input_driver.cpp"
presenter_file = sdk / "src/ui/vulkan/vulkan_presenter.cpp"
for path in (input_file, presenter_file):
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

print("[recvx-android-input-fps] touch gamepad is routed as a synthetic user-0 device")
print("[recvx-android-input-fps] successful Vulkan presentations are sampled every 2 seconds and exported for the overlay")
