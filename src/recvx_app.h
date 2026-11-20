// Resident Evil Code: Veronica X HD - ReXGlue runtime integration

#pragma once

#include <algorithm>
#include <atomic>
#include <chrono>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <memory>
#include <thread>
#include <vector>

#if defined(__ANDROID__)
extern "C" void RecvX_ShutdownTouchGamepad();
#endif

#include <rex/logging.h>
#include <rex/rex_app.h>
#include <rex/system/interfaces/graphics.h>
#include <rex/ui/presenter.h>

#include <imgui.h>

class RecvXInGameDialog final : public rex::ui::ImGuiDialog {
 public:
  explicit RecvXInGameDialog(rex::ui::ImGuiDrawer* drawer)
      : rex::ui::ImGuiDialog(drawer) {}

 protected:
  void OnDraw(ImGuiIO& io) override {
    const ImVec2 button_size(92.0f, 42.0f);
    ImGui::SetNextWindowPos(ImVec2(io.DisplaySize.x - button_size.x - 16.0f,
                                   io.DisplaySize.y - button_size.y - 16.0f), ImGuiCond_Always);
    ImGui::SetNextWindowSize(button_size, ImGuiCond_Always);
    constexpr ImGuiWindowFlags button_flags = ImGuiWindowFlags_NoDecoration |
        ImGuiWindowFlags_NoSavedSettings | ImGuiWindowFlags_NoFocusOnAppearing |
        ImGuiWindowFlags_NoNav;
    if (ImGui::Begin("RECVX Menu Button##recvx", nullptr, button_flags)) {
      if (ImGui::Button(menu_open_ ? "FECHAR" : "MENU", ImVec2(-1.0f, -1.0f)))
        menu_open_ = !menu_open_;
    }
    ImGui::End();
    if (!menu_open_) return;

    ImGui::SetNextWindowSize(ImVec2(420.0f, 360.0f), ImGuiCond_FirstUseEver);
    ImGui::SetNextWindowPos(ImVec2(io.DisplaySize.x * 0.5f, io.DisplaySize.y * 0.5f),
                            ImGuiCond_FirstUseEver, ImVec2(0.5f, 0.5f));
    if (!ImGui::Begin("RESIDENT EVIL CODE: VERONICA X##recvx_menu", &menu_open_,
                      ImGuiWindowFlags_NoCollapse)) { ImGui::End(); return; }
    if (ImGui::BeginTabBar("##recvx_tabs")) {
      if (ImGui::BeginTabItem("Cheats")) {
        ImGui::TextWrapped("Opcoes de treinador para este XEX");
        ImGui::Separator();
        ImGui::BeginDisabled();
        bool infinite_health = false, infinite_ammo = false;
        bool chest_items = false, time_control = false;
        ImGui::Checkbox("Vida infinita", &infinite_health);
        ImGui::Checkbox("Municao infinita", &infinite_ammo);
        ImGui::Checkbox("Itens no bau", &chest_items);
        ImGui::Checkbox("Controle do tempo", &time_control);
        ImGui::EndDisabled();
        ImGui::TextDisabled("Desativado: enderecos/codigos ainda nao validados para Bio_cv.exe.");
        ImGui::EndTabItem();
      }
      if (ImGui::BeginTabItem("Salvar / Carregar")) {
        ImGui::TextWrapped("Save convencional do Code Veronica X");
        ImGui::Separator();
        ImGui::BeginDisabled();
        ImGui::Button("Salvar jogo", ImVec2(-1.0f, 42.0f));
        ImGui::Button("Carregar jogo", ImVec2(-1.0f, 42.0f));
        ImGui::EndDisabled();
        ImGui::TextWrapped("Salvar normalmente exige maquina de escrever e Ink Ribbon. Carregar usa LOAD GAME na tela de titulo.");
        ImGui::TextDisabled("A integracao XAM ainda nao e segura: OpenFile retorna FILE_NOT_FOUND e Flush e no-op no SDK auditado.");
        ImGui::EndTabItem();
      }
      if (ImGui::BeginTabItem("Continuar")) {
        ImGui::TextWrapped("Fechar somente o painel e voltar ao jogo.");
        if (ImGui::Button("VOLTAR AO JOGO", ImVec2(-1.0f, 48.0f))) menu_open_ = false;
        ImGui::EndTabItem();
      }
      ImGui::EndTabBar();
    }
    ImGui::End();
  }
 private:
  bool menu_open_ = false;
};


class RecvXApp : public rex::ReXApp {
 public:
  using rex::ReXApp::ReXApp;

  static std::unique_ptr<rex::ui::WindowedApp> Create(
      rex::ui::WindowedAppContext& ctx) {
    return std::unique_ptr<RecvXApp>(
        new RecvXApp(ctx, "recvx", PPCImageConfig));
  }

 protected:
  void OnCreateDialogs(rex::ui::ImGuiDrawer* drawer) override {
    // O drawer mantem este overlay anexado durante toda a execucao do jogo.
    new RecvXInGameDialog(drawer);
  }

  void OnPostSetup() override {
    if (rex::cvar::GetFlagSource("snorm16_render_target_full_range") ==
        rex::cvar::Source::kDefault) {
      rex::cvar::SetFlagByName("snorm16_render_target_full_range", "false");
    }
    REXLOG_INFO("[GPU] snorm16_render_target_full_range = {}",
                rex::cvar::GetFlagByName("snorm16_render_target_full_range"));
  }

  void OnPreSetup(rex::RuntimeConfig& config) override {
    // Explicitly enable the Xenos GPU plugin for the Android runtime.
    config.gpu_plugin = "xenos";
  }

  void OnLoadXexImage(std::string& xex_image) override {
    // Keep the original case for case-sensitive Linux filesystems.
    xex_image = "game:\\Default.xex";
  }

  void OnPostLaunchModule(rex::system::XThread* thread) override {
    (void)thread;
    capture_stop_.store(false, std::memory_order_release);
    capture_thread_ = std::thread([this]() { CaptureFirstVisibleGuestFrame(); });
  }

  void OnShutdown() override {
    capture_stop_.store(true, std::memory_order_release);
    if (capture_thread_.joinable()) {
      capture_thread_.join();
    }
#if defined(__ANDROID__)
    RecvX_ShutdownTouchGamepad();
#endif
  }

 private:
  void CaptureFirstVisibleGuestFrame() {
    bool guest_output_seen = false;
    for (unsigned attempt = 0;
         attempt < 1200 && !capture_stop_.load(std::memory_order_acquire);
         ++attempt) {
      auto* current_runtime = runtime();
      auto* graphics = current_runtime ? current_runtime->graphics_system() : nullptr;
      auto* presenter = graphics ? graphics->presenter() : nullptr;
      rex::ui::RawImage image;
      if (!presenter || !presenter->CaptureGuestOutput(image)) {
        std::this_thread::sleep_for(std::chrono::milliseconds(25));
        continue;
      }

      const size_t minimum_stride = size_t(image.width) * 4;
      const size_t required_size = image.height
                                       ? image.stride * size_t(image.height - 1) +
                                             minimum_stride
                                       : 0;
      if (!image.width || !image.height || image.stride < minimum_stride ||
          image.data.size() < required_size) {
        REXLOG_ERROR(
            "[GPU] RECVX guest output has invalid storage: {}x{}, stride={}, bytes={}",
            image.width, image.height, image.stride, image.data.size());
        return;
      }

      size_t non_black_pixels = 0;
      uint8_t minimum_channel = 255;
      uint8_t maximum_channel = 0;
      uint64_t checksum = 1469598103934665603ull;
      for (uint32_t y = 0; y < image.height; ++y) {
        const uint8_t* row = image.data.data() + image.stride * size_t(y);
        for (uint32_t x = 0; x < image.width; ++x) {
          const uint8_t* pixel = row + size_t(x) * 4;
          non_black_pixels += (pixel[0] | pixel[1] | pixel[2]) != 0;
          for (unsigned channel = 0; channel < 3; ++channel) {
            minimum_channel = std::min(minimum_channel, pixel[channel]);
            maximum_channel = std::max(maximum_channel, pixel[channel]);
            checksum = (checksum ^ pixel[channel]) * 1099511628211ull;
          }
        }
      }

      if (!guest_output_seen) {
        guest_output_seen = true;
        REXLOG_INFO(
            "[GPU] RECVX first guest output reached Presenter: {}x{}, stride={}",
            image.width, image.height, image.stride);
      }

      if (!non_black_pixels || maximum_channel < 16 ||
          unsigned(maximum_channel - minimum_channel) < 8) {
        std::this_thread::sleep_for(std::chrono::milliseconds(25));
        continue;
      }

      REXLOG_INFO(
          "[GPU] RECVX FIRST VISIBLE FRAME: non_black={}/{}, channel_range={}-{}, rgb_fnv1a={:016X}",
          non_black_pixels, size_t(image.width) * image.height, minimum_channel,
          maximum_channel, checksum);

      const char* capture_path = std::getenv("RECVX_CAPTURE_FIRST_FRAME");
      if (capture_path && *capture_path) {
        const std::filesystem::path output_path(capture_path);
        std::error_code directory_error;
        if (!output_path.parent_path().empty()) {
          std::filesystem::create_directories(output_path.parent_path(),
                                              directory_error);
        }
        std::ofstream output(output_path, std::ios::binary | std::ios::trunc);
        if (!directory_error && output) {
          output << "P6\n" << image.width << ' ' << image.height << "\n255\n";
          std::vector<uint8_t> rgb(size_t(image.width) * image.height * 3);
          for (uint32_t y = 0; y < image.height; ++y) {
            const uint8_t* source = image.data.data() + image.stride * size_t(y);
            uint8_t* destination = rgb.data() + size_t(y) * image.width * 3;
            for (uint32_t x = 0; x < image.width; ++x) {
              destination[size_t(x) * 3 + 0] = source[size_t(x) * 4 + 0];
              destination[size_t(x) * 3 + 1] = source[size_t(x) * 4 + 1];
              destination[size_t(x) * 3 + 2] = source[size_t(x) * 4 + 2];
            }
          }
          output.write(reinterpret_cast<const char*>(rgb.data()),
                       static_cast<std::streamsize>(rgb.size()));
          if (output) {
            REXLOG_INFO("[GPU] captured RECVX guest frame to {}",
                        output_path.string());
          }
        }
      }
      return;
    }

    if (!capture_stop_.load(std::memory_order_acquire)) {
      REXLOG_WARN(guest_output_seen
                      ? "[GPU] RECVX guest output stayed black/flat for 30 seconds"
                      : "[GPU] RECVX produced no capturable guest output in 30 seconds");
    }
  }

  std::atomic<bool> capture_stop_{false};
  std::thread capture_thread_;
};
