# Status

## Current phase

Initial ReXGlue bring-up scaffold for the supported PAL Xbox 360 XEX.

## Verified target facts

- Title ID: `43430822`
- Media ID: `58A6EFFB`
- Internal module string: `Bio_cv.exe`
- XEX SHA-256: `c552c6995462a5cefdd52c07bebd28fff4481164b19a445c636d7b54736f3c70`
- ReXGlue baseline: `0.10.0-dev.g398e2ba`

## Not yet claimed

- successful full codegen
- complete function registration
- guest entrypoint execution
- rendered frame
- audio correctness
- controller input
- gameplay

Those milestones should only be checked off from logs produced by this exact
project and XEX.

## Local XEX verification

The user verified the local game file on an Android/Termux device on 2026-10-21:

- File: `Default.xex`
- Size: `13774848` bytes
- Header: `XEX2`
- SHA-256: `c552c6995462a5cefdd52c07bebd28fff4481164b19a445c636d7b54736f3c70` (matches the expected target hash above)
- ASCII module references found: `Bio_cv.exe`, `xam.xex`, `xboxkrnl.exe`

This is a local-file identity check only. The retail XEX is intentionally not committed to this repository, and this check does not demonstrate successful code generation, Android compilation, or gameplay.

## Android ARM64 blocker confirmed (2026-10-25)

The latest GitHub Actions run, [Android ARM64 platform probe](https://github.com/marcussilvacastrooutlok-afk/recomp-codeveronica/actions/runs/40219955322), successfully configured CMake but correctly failed its platform validation. The pinned SDK commit `398e2ba7802d0c4ca1f68d7ad4fa2cd73e8123eb` selected `Platform: linux-arm64` and defines `REX_PLATFORM_LINUX=1` even when configured with the Android NDK. Therefore this run is **not** an Android build and did not produce an APK.

Source inspection of that pinned SDK also confirms the problem is larger than the platform label:

- Top-level platform detection explicitly supports Windows, Linux, and macOS only.
- `src/ui/CMakeLists.txt` always compiles the desktop `window_sdl.cpp`, `windowed_app.cpp`, and `windowed_app_context_sdl.cpp` path.
- The non-Apple Unix UI branch requires Linux X11-XCB and Wayland dependencies, which are host libraries and cannot be used as Android NDK replacements.
- The app entrypoint currently uses ReXGlue's desktop SDL windowed-app bootstrap.

### Required engineering work before an APK can be claimed

1. Add a real Android platform selection and Android compile definitions in the SDK build configuration.
2. Implement or adapt the UI/window/surface integration for Android's SDL Activity/native lifecycle and Vulkan surface; exclude Linux X11/Wayland source and link dependencies on Android.
3. Add an Android app/library packaging workflow that builds ARM64 native libraries and packages SDL Java/JNI components, then checks all shared-library dependencies.
4. Only after the Android native target links should the workflow produce an APK and validate its launch; the game XEX and gameplay remain separate verification steps.

Do not bypass the platform validation or rename Linux ARM64 as Android. This status records a confirmed upstream SDK limitation, not a completed Android port.


## Linux code generation and native build verified (2026-10-25)

The GitHub Actions run [Resident Evil codegen diagnostic](https://github.com/marcussilvacastrooutlok-afk/recomp-codeveronica/actions/runs/40191411586) completed successfully with the exact XEX SHA-256 recorded above. The job generated and compiled the title-specific C++ output (214 compilation units shown in the build log), linked the Linux x86-64 executable `recvx`, and staged `librexgpu-xenos.so` and `librexruntime.so`. This confirms the current manifest/codegen path can produce a Linux executable for this XEX; it does not confirm Android compatibility or gameplay.

The next blocker remains Android platform support in the pinned ReXGlue SDK. The Android NDK configure probe [run 40219955322](https://github.com/marcussilvacastrooutlok-afk/recomp-codeveronica/actions/runs/40219955322) configured CMake but selected `Platform: linux-arm64`, so it was correctly rejected. Do not package the Linux executable or Linux shared libraries as an Android APK. The next implementation step is a real Android platform/window/surface integration, followed by an ARM64 native link and APK packaging.
