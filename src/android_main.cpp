// Android entry point for the ReXGlue SDL application.
// SDLActivity loads libSDL3.so and libmain.so, then invokes SDL_main on
// SDL's application thread. Keep this separate from the desktop main().
#include <SDL3/SDL_main.h>
#include <SDL3/SDL_log.h>
#include <SDL3/SDL_filesystem.h>
#include <SDL3/SDL_stdinc.h>
#include <SDL3/SDL_system.h>
#include <SDL3/SDL_gamepad.h>
#include <SDL3/SDL_joystick.h>
#include <SDL3/SDL_events.h>
#include <SDL3/SDL_init.h>

#include <jni.h>
#include <filesystem>

#include <cstdlib>
#include <exception>
#include <map>
#include <memory>
#include <mutex>
#include <algorithm>
#include <string>
#include <vector>

#include <rex/cvar.h>
#include <rex/logging.h>
#include <rex/ui/windowed_app.h>
#include <rex/ui/windowed_app_context_sdl.h>

namespace {

std::mutex g_touch_joystick_mutex;
SDL_Joystick* g_touch_joystick = nullptr;
SDL_JoystickID g_touch_joystick_id = 0;
bool g_touch_joystick_attempted = false;

bool EnsureTouchJoystickLocked() {
  if (g_touch_joystick) return true;
  if (g_touch_joystick_attempted) return false;
  g_touch_joystick_attempted = true;

  if (!SDL_InitSubSystem(SDL_INIT_GAMEPAD)) {
    SDL_Log("[RECVX-TOUCH] SDL gamepad subsystem initialization failed: %s", SDL_GetError());
    return false;
  }

  SDL_VirtualJoystickDesc desc;
  SDL_INIT_INTERFACE(&desc);
  desc.type = SDL_JOYSTICK_TYPE_GAMEPAD;
  desc.vendor_id = 0x1209;
  desc.product_id = 0x0001;
  desc.naxes = SDL_GAMEPAD_AXIS_COUNT;
  desc.nbuttons = SDL_GAMEPAD_BUTTON_COUNT;
  desc.button_mask = (1u << SDL_GAMEPAD_BUTTON_COUNT) - 1u;
  desc.axis_mask = (1u << SDL_GAMEPAD_AXIS_COUNT) - 1u;
  desc.name = "Resident Evil Code Veronica Touch";

  g_touch_joystick_id = SDL_AttachVirtualJoystick(&desc);
  if (!g_touch_joystick_id) {
    SDL_Log("[RECVX-TOUCH] Could not attach virtual gamepad: %s", SDL_GetError());
    return false;
  }

  g_touch_joystick = SDL_OpenJoystick(g_touch_joystick_id);
  if (!g_touch_joystick) {
    SDL_Log("[RECVX-TOUCH] Could not open virtual gamepad: %s", SDL_GetError());
    SDL_DetachVirtualJoystick(g_touch_joystick_id);
    g_touch_joystick_id = 0;
    return false;
  }

  SDL_Log("[RECVX-TOUCH] Virtual gamepad attached (instance=%u)",
          static_cast<unsigned>(g_touch_joystick_id));
  SDL_PumpEvents();
  return true;
}

bool ConfigureAndroidRuntimeDataDirectory() {
  auto* env = static_cast<JNIEnv*>(SDL_GetAndroidJNIEnv());
  auto activity = static_cast<jobject>(SDL_GetAndroidActivity());
  if (!env || !activity) {
    SDL_Log("[RECVX-DIAG] Android activity/JNI environment unavailable");
    return false;
  }

  jclass activity_class = env->GetObjectClass(activity);
  if (!activity_class || env->ExceptionCheck()) {
    if (env->ExceptionCheck()) env->ExceptionClear();
    env->DeleteLocalRef(activity);
    return false;
  }

  jmethodID get_external_files_dir = env->GetMethodID(
      activity_class, "getExternalFilesDir", "(Ljava/lang/String;)Ljava/io/File;");
  if (!get_external_files_dir || env->ExceptionCheck()) {
    if (env->ExceptionCheck()) env->ExceptionClear();
    env->DeleteLocalRef(activity_class);
    env->DeleteLocalRef(activity);
    return false;
  }

  jobject directory = env->CallObjectMethod(activity, get_external_files_dir, nullptr);
  if (env->ExceptionCheck()) {
    env->ExceptionClear();
    directory = nullptr;
  }

  std::string base_path;
  if (directory) {
    jclass file_class = env->GetObjectClass(directory);
    jmethodID get_absolute_path = file_class ? env->GetMethodID(
        file_class, "getAbsolutePath", "()Ljava/lang/String;") : nullptr;
    jstring path_string = get_absolute_path
        ? static_cast<jstring>(env->CallObjectMethod(directory, get_absolute_path))
        : nullptr;
    if (env->ExceptionCheck()) {
      env->ExceptionClear();
      path_string = nullptr;
    }
    if (path_string) {
      const char* chars = env->GetStringUTFChars(path_string, nullptr);
      if (chars) {
        base_path = chars;
        env->ReleaseStringUTFChars(path_string, chars);
      }
      env->DeleteLocalRef(path_string);
    }
    if (file_class) env->DeleteLocalRef(file_class);
    env->DeleteLocalRef(directory);
  }

  env->DeleteLocalRef(activity_class);
  env->DeleteLocalRef(activity);

  // Prefer /storage/emulated/0/Android/data/<package>/files. If Android
  // reports external storage unavailable, fall back to SDL's app-private
  // writable preference directory rather than using /data/.local.
  if (base_path.empty()) {
    char* pref_path = SDL_GetPrefPath("ReXGlue", "recvx");
    if (pref_path) {
      base_path = pref_path;
      SDL_free(pref_path);
    }
  }
  if (base_path.empty()) {
    SDL_Log("[RECVX-DIAG] Could not resolve an app-writable data directory");
    return false;
  }

  const std::filesystem::path root_path =
      std::filesystem::path(base_path) / "rexglue";
  const std::filesystem::path home_path = root_path / "home";
  const std::filesystem::path data_path = root_path / "data";
  const std::filesystem::path config_path = root_path / "config";
  const std::filesystem::path cache_path = root_path / "cache";
  const std::filesystem::path state_path = root_path / "state";

  std::error_code ec;
  for (const auto& directory :
       {home_path, data_path, config_path, cache_path, state_path}) {
    std::filesystem::create_directories(directory, ec);
    if (ec) {
      SDL_Log("[RECVX-DIAG] Could not create runtime directory %s: %s",
              directory.string().c_str(), ec.message().c_str());
      return false;
    }
  }

  // Keep all standard Unix/XDG locations inside this app's Android/data
  // directory. This prevents HOME=/data from producing forbidden /data/.local.
  if (setenv("HOME", home_path.c_str(), 1) != 0 ||
      setenv("XDG_DATA_HOME", data_path.c_str(), 1) != 0 ||
      setenv("XDG_CONFIG_HOME", config_path.c_str(), 1) != 0 ||
      setenv("XDG_CACHE_HOME", cache_path.c_str(), 1) != 0 ||
      setenv("XDG_STATE_HOME", state_path.c_str(), 1) != 0) {
    SDL_Log("[RECVX-DIAG] Failed to configure Android HOME/XDG directories");
    return false;
  }
  SDL_Log("[RECVX-DIAG] Android runtime storage root: %s",
          root_path.string().c_str());
  SDL_Log("[RECVX-DIAG] HOME=%s", home_path.string().c_str());
  SDL_Log("[RECVX-DIAG] XDG_DATA_HOME=%s", data_path.string().c_str());
  return true;
}

}  // namespace

extern "C" float ReXGlue_GetPresentedFPS();

extern "C" JNIEXPORT jfloat JNICALL
Java_org_libsdl_app_GameSDLActivity_nativeGetPresentedFps(JNIEnv*, jclass) {
  return static_cast<jfloat>(ReXGlue_GetPresentedFPS());
}

extern "C" JNIEXPORT void JNICALL
Java_org_libsdl_app_GameSDLActivity_nativeSetTouchButton(
    JNIEnv*, jclass, jint button, jboolean pressed) {
  if (button < 0 || button >= SDL_GAMEPAD_BUTTON_COUNT) return;
  std::lock_guard<std::mutex> lock(g_touch_joystick_mutex);
  if (!EnsureTouchJoystickLocked()) return;
  if (!SDL_SetJoystickVirtualButton(g_touch_joystick, button, pressed == JNI_TRUE)) {
    SDL_Log("[RECVX-TOUCH] Virtual button update failed: %s", SDL_GetError());
    return;
  }
  SDL_PumpEvents();
}

extern "C" JNIEXPORT void JNICALL
Java_org_libsdl_app_GameSDLActivity_nativeSetTouchAxis(
    JNIEnv*, jclass, jint axis, jfloat value) {
  if (axis < 0 || axis >= SDL_GAMEPAD_AXIS_COUNT) return;
  const float clamped = std::max(-1.0f, std::min(1.0f, value));
  const auto scaled = static_cast<Sint16>(clamped <= -1.0f ? -32768
                                  : clamped >= 1.0f ? 32767
                                  : clamped * 32767.0f);
  std::lock_guard<std::mutex> lock(g_touch_joystick_mutex);
  if (!EnsureTouchJoystickLocked()) return;
  if (!SDL_SetJoystickVirtualAxis(g_touch_joystick, axis, scaled)) {
    SDL_Log("[RECVX-TOUCH] Virtual axis update failed: %s", SDL_GetError());
    return;
  }
  SDL_PumpEvents();
}

extern "C" void RecvX_ShutdownTouchGamepad() {
  std::lock_guard<std::mutex> lock(g_touch_joystick_mutex);
  if (g_touch_joystick) {
    SDL_CloseJoystick(g_touch_joystick);
    g_touch_joystick = nullptr;
  }
  if (g_touch_joystick_id) {
    SDL_DetachVirtualJoystick(g_touch_joystick_id);
    g_touch_joystick_id = 0;
  }
  g_touch_joystick_attempted = false;
}

extern "C" int SDL_main(int argc, char* argv[]) {
  SDL_Log("[RECVX-DIAG] SDL_main entered: argc=%d", argc);
  for (int i = 0; i < argc; ++i) SDL_Log("[RECVX-DIAG] argv[%d]=%s", i, argv && argv[i] ? argv[i] : "<null>");

  // ReXGlue GetUserFolder() honors XDG_DATA_HOME before falling back to
  // HOME/.local/share or the Android passwd home (/data). Set it before
  // cvar/runtime initialization so Xenos and the runtime use app storage.
  if (!ConfigureAndroidRuntimeDataDirectory()) return EXIT_FAILURE;

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
  SDL_Log("[RECVX-INPUT] initializing SDL gamepad subsystem");
  if (!SDL_InitSubSystem(SDL_INIT_GAMEPAD)) {
    SDL_Log("[RECVX-INPUT] SDL_INIT_GAMEPAD failed: %s", SDL_GetError());
  } else {
    SDL_Log("[RECVX-INPUT] SDL gamepad subsystem ready");
  }

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
