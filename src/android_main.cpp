// Android entry point for the ReXGlue SDL application.
// SDLActivity loads libSDL3.so and libmain.so, then invokes SDL_main on
// SDL's application thread. Keep this separate from the desktop main().
#include <SDL3/SDL_main.h>
#include <SDL3/SDL_log.h>
#include <SDL3/SDL_filesystem.h>
#include <SDL3/SDL_stdinc.h>

#include <cstdlib>
#include <exception>
#include <map>
#include <memory>
#include <algorithm>
#include <string>
#include <vector>

#include <rex/cvar.h>
#include <rex/logging.h>
#include <rex/ui/windowed_app.h>
#include <rex/ui/windowed_app_context_sdl.h>

extern "C" int SDL_main(int argc, char* argv[]) {
  SDL_Log("[RECVX-DIAG] SDL_main entered: argc=%d", argc);
  for (int i = 0; i < argc; ++i) SDL_Log("[RECVX-DIAG] argv[%d]=%s", i, argv && argv[i] ? argv[i] : "<null>");

  // ReXGlue's default log directory is based on the executable folder. On
  // Android that can resolve to /system/bin, which is read-only. Give the
  // logger an explicit file inside SDL's app-private writable preference dir.
  char* pref_path = SDL_GetPrefPath("ReXGlue", "recvx");
  if (!pref_path) {
    SDL_Log("[RECVX-DIAG] SDL_GetPrefPath failed: %s", SDL_GetError());
    return EXIT_FAILURE;
  }
  std::string log_file_arg = std::string("--log_file=") + pref_path + "recvx.log";
  SDL_free(pref_path);

  // Preserve an explicitly supplied log_file option; otherwise append the
  // Android-safe path before cvar initialization.
  bool has_log_file_arg = false;
  for (int i = 1; i < argc; ++i) {
    if (argv && argv[i] &&
        (std::string(argv[i]).starts_with("--log_file=") ||
         std::string(argv[i]) == "--log_file")) {
      has_log_file_arg = true;
      break;
    }
  }

  std::vector<char*> cvar_argv;
  cvar_argv.reserve(static_cast<size_t>(argc) + (has_log_file_arg ? 0 : 1));
  for (int i = 0; i < argc; ++i) cvar_argv.push_back(argv[i]);
  if (!has_log_file_arg) {
    cvar_argv.push_back(log_file_arg.data());
    SDL_Log("[RECVX-DIAG] Android log file: %s", log_file_arg.c_str() + 11);
  }

  // Match the SDK's desktop entry point: preserve positional arguments and
  // pass them to WindowedApp before initialization.
  auto remaining = rex::cvar::Init(static_cast<int>(cvar_argv.size()), cvar_argv.data());
  SDL_Log("[RECVX-DIAG] cvar::Init complete; remaining=%zu", remaining.size());
  rex::cvar::ApplyEnvironment();
  rex::InitLoggingEarly();
  SDL_Log("[RECVX-DIAG] cvars and early logging initialized");

  int result = EXIT_FAILURE;
  rex::ui::SDLWindowedAppContext context;
  SDL_Log("[RECVX-DIAG] initializing SDL window context");
  if (!context.Initialize()) {
    REXLOG_ERROR("[Android] SDLWindowedAppContext initialization failed");
    return result;
  }

  SDL_Log("[RECVX-DIAG] SDL window context initialized");
  const auto creator = rex::ui::WindowedApp::GetCreator("recvx");
  if (!creator) {
    REXLOG_ERROR("[Android] ReXGlue application creator 'recvx' was not registered");
    return result;
  }

  SDL_Log("[RECVX-DIAG] recvx creator found");
  std::unique_ptr<rex::ui::WindowedApp> app;
  try {
    app = creator(context);
  } catch (...) {
    REXLOG_ERROR("[Android] Creating the ReXGlue application threw an exception");
    return result;
  }
  if (!app) {
    REXLOG_ERROR("[Android] ReXGlue application creator returned null");
    return result;
  }

  SDL_Log("[RECVX-DIAG] recvx app instance created");
  // Match the official SDK entry point's positional-option mapping.
  const auto& option_names = app->GetPositionalOptions();
  std::map<std::string, std::string> parsed;
  const size_t count = std::min(remaining.size(), option_names.size());
  for (size_t i = 0; i < count; ++i) {
    parsed[option_names[i]] = remaining[i];
  }
  app->SetParsedArguments(std::move(parsed));
  SDL_Log("[RECVX-DIAG] positional arguments assigned; calling OnInitialize");

  bool initialize_attempted = false;
  try {
    initialize_attempted = true;
    if (app->OnInitialize()) {
      SDL_Log("[RECVX-DIAG] OnInitialize succeeded; entering SDL main loop");
      result = context.RunMainMessageLoop();
      SDL_Log("[RECVX-DIAG] SDL main loop returned: result=%d", result);
    } else {
      SDL_Log("[RECVX-DIAG] OnInitialize returned false");
      REXLOG_ERROR("[Android] ReXGlue application OnInitialize() failed");
    }
    // Required even after a partial initialization that returned false.
    SDL_Log("[RECVX-DIAG] invoking app destruction");
    app->InvokeOnDestroy();
  } catch (const std::exception& e) {
    SDL_Log("[RECVX-DIAG] std::exception during app lifecycle: %s", e.what());
    REXLOG_ERROR("[Android] Exception during ReXGlue application lifecycle: {}", e.what());
    if (initialize_attempted) {
      try {
        SDL_Log("[RECVX-DIAG] invoking app destruction after std::exception");
        app->InvokeOnDestroy();
      } catch (const std::exception& destroy_error) {
        SDL_Log("[RECVX-DIAG] std::exception during destruction: %s", destroy_error.what());
      } catch (...) {
        SDL_Log("[RECVX-DIAG] unknown exception during destruction");
      }
    }
    result = EXIT_FAILURE;
  } catch (...) {
    SDL_Log("[RECVX-DIAG] unknown non-std exception during app lifecycle");
    REXLOG_ERROR("[Android] Unknown exception during ReXGlue application lifecycle");
    if (initialize_attempted) {
      try {
        app->InvokeOnDestroy();
      } catch (const std::exception& destroy_error) {
        SDL_Log("[RECVX-DIAG] std::exception during destruction: %s", destroy_error.what());
      } catch (...) {
        SDL_Log("[RECVX-DIAG] unknown exception during destruction");
      }
    }
    result = EXIT_FAILURE;
  }
  SDL_Log("[RECVX-DIAG] SDL_main exiting: result=%d", result);
  return result;
}
