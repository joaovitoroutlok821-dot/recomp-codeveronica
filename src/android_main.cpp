// Android entry point for the ReXGlue SDL application.
// SDLActivity loads libSDL3.so and libmain.so, then invokes SDL_main on
// SDL's application thread. Keep this separate from the desktop main().
#include <SDL3/SDL_main.h>

#include <cstdlib>
#include <memory>

#include <rex/cvar.h>
#include <rex/logging.h>
#include <rex/ui/windowed_app.h>
#include <rex/ui/windowed_app_context_sdl.h>

extern "C" int SDL_main(int argc, char* argv[]) {
  // SDL supplies the process arguments to SDL_main. Reuse ReXGlue's normal
  // cvar parser, but do not depend on a desktop shell or executable entrypoint.
  rex::cvar::Init(argc, argv);
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

  bool initialized = false;
  try {
    initialized = app->OnInitialize();
    if (initialized) {
      result = context.RunMainMessageLoop();
    } else {
      REXLOG_ERROR("[Android] ReXGlue application OnInitialize() failed");
    }
    // The SDK contract requires this after every OnInitialize() attempt,
    // including a partial initialization that returned false.
    app->InvokeOnDestroy();
  } catch (...) {
    REXLOG_ERROR("[Android] Exception during ReXGlue application lifecycle");
    if (initialized) {
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
