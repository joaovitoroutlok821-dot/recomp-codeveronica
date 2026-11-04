// Android entry point for the ReXGlue SDL application.
// SDLActivity loads libSDL3.so and libmain.so, then invokes SDL_main on
// SDL's application thread. Keep this separate from the desktop main().
#include <SDL3/SDL_main.h>

#include <cstdlib>
#include <map>
#include <memory>
#include <algorithm>

#include <rex/cvar.h>
#include <rex/logging.h>
#include <rex/ui/windowed_app.h>
#include <rex/ui/windowed_app_context_sdl.h>

extern "C" int SDL_main(int argc, char* argv[]) {
  // Match the SDK's desktop entry point: preserve positional arguments and
  // pass them to WindowedApp before initialization.
  auto remaining = rex::cvar::Init(argc, argv);
  rex::cvar::ApplyEnvironment();
  rex::InitLoggingEarly();

  int result = EXIT_FAILURE;
  rex::ui::SDLWindowedAppContext context;
  if (!context.Initialize()) {
    REXLOG_ERROR("[Android] SDLWindowedAppContext initialization failed");
    return result;
  }

  const auto creator = rex::ui::WindowedApp::GetCreator("recvx");
  if (!creator) {
    REXLOG_ERROR("[Android] ReXGlue application creator 'recvx' was not registered");
    return result;
  }

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

  // Match the official SDK entry point's positional-option mapping.
  const auto& option_names = app->GetPositionalOptions();
  std::map<std::string, std::string> parsed;
  const size_t count = std::min(remaining.size(), option_names.size());
  for (size_t i = 0; i < count; ++i) {
    parsed[option_names[i]] = remaining[i];
  }
  app->SetParsedArguments(std::move(parsed));

  bool initialize_attempted = false;
  try {
    initialize_attempted = true;
    if (app->OnInitialize()) {
      result = context.RunMainMessageLoop();
    } else {
      REXLOG_ERROR("[Android] ReXGlue application OnInitialize() failed");
    }
    // Required even after a partial initialization that returned false.
    app->InvokeOnDestroy();
  } catch (...) {
    REXLOG_ERROR("[Android] Exception during ReXGlue application lifecycle");
    if (initialize_attempted) {
      try {
        app->InvokeOnDestroy();
      } catch (...) {
        REXLOG_ERROR("[Android] Exception while destroying ReXGlue application");
      }
    }
    result = EXIT_FAILURE;
  }
  return result;
}
