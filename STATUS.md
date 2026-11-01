# Status

## Current phase

Android ARM64 SDK integration is compiling; the next phase is linking the title-specific Resident Evil target and completing SDL Activity/Vulkan surface integration and APK packaging.

## Verified target facts

- Title ID: `43430822`
- Media ID: `58A6EFFB`
- Internal module string: `Bio_cv.exe`
- XEX SHA-256: `c552c6995462a5cefdd52c07bebd28fff4481164b19a445c636d7b54736f3c70`
- ReXGlue baseline: `0.10.0-dev.g398e2ba`

## Android ARM64 SDK compile verified (2026-10-29)

GitHub Actions run [40925144992](https://github.com/marcussilvacastrooutlok-afk/recomp-codeveronica/actions/runs/40925144992), commit `ef6f1a3f71fd1b180fdaec759d52a280325bb142`, completed the Android NDK build. The archived `compile_commands.json` proves the compiler target is `aarch64-none-linux-android26` and the compile definitions include `REX_PLATFORM_ANDROID=1`; this is not a Linux ARM64 build mislabeled as Android.

The build log reached step 790/791 and linked at least:
- `librexruntime.so`
- `librexgpu-xenos.so`
- Android ARM64 `rexglue` executable

This is an SDK-level milestone only. The artifact contains logs and build metadata, not the compiled binaries. It does **not** yet prove that the game-specific `recvx` target links for Android, that the SDL Activity lifecycle and Vulkan surface work on-device, that an APK is packaged, or that the game renders.

### Remaining Android work

1. Build the title-specific generated C++ target for `arm64-v8a` against the Android SDK build.
2. Validate every shared-library dependency and package SDL Java/JNI plus the native libraries into an APK.
3. Verify Android Activity lifecycle, Vulkan surface creation/resume/pause, and storage access.
4. Install and launch on the user's Android device; then test rendering, audio, and controls separately.

## Local XEX verification

The user verified the local game file on an Android/Termux device on 2026-10-21:

- File: `Default.xex`
- Size: `13774848` bytes
- Header: `XEX2`
- SHA-256: `c552c6995462a5cefdd52c07bebd28fff4481164b19a445c636d7b54736f3c70`
- ASCII module references: `Bio_cv.exe`, `xam.xex`, `xboxkrnl.exe`

The retail XEX is intentionally not committed to this repository. This identity check does not demonstrate Android gameplay.

## Linux code generation and native build verified (2026-10-25)

The Linux diagnostic completed successfully with the exact XEX hash recorded above. It generated and compiled 214 title-specific C++ compilation units, linked the Linux x86-64 executable `recvx`, and staged `librexgpu-xenos.so` and `librexruntime.so`. This does not confirm Android compatibility or gameplay.

## Historical Android blocker (2026-10-25)

The earlier run [40219955322](https://github.com/marcussilvacastrooutlok-afk/recomp-codeveronica/actions/runs/40219955322) selected `linux-arm64` despite use of the Android NDK and was correctly rejected. That blocker is superseded by the successful Android ARM64 compile in run 40925144992. The old run must not be treated as the current platform result.

## Not yet verified

- Android title-specific `recvx` shared-library link
- APK packaging and install
- guest entrypoint execution on Android
- rendered frame
- audio correctness
- controller input
- gameplay
