#!/usr/bin/env python3
"""Apply the minimal Android ARM64 platform/UI compatibility layer to pinned ReXGlue."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: ensure-rexglue-android-platform.py /path/to/rexglue-sdk")
root = Path(sys.argv[1]).resolve()

def edit(rel, old, new, label):
    p = root / rel
    if not p.is_file():
        raise SystemExit(f"[android-platform] missing file: {rel}")
    s = p.read_text(encoding="utf-8")
    if new in s:
        return
    if old not in s:
        raise SystemExit(f"[android-platform] expected anchor not found in {rel}: {label}")
    p.write_text(s.replace(old, new, 1), encoding="utf-8")

edit("CMakeLists.txt",
'''elseif(UNIX AND NOT APPLE)
    if(REX_TARGET_PROCESSOR MATCHES "AMD64|x86_64")''',
'''elseif(ANDROID)
    if(REX_TARGET_PROCESSOR MATCHES "aarch64|ARM64|arm64")
        set(REX_PLATFORM "android-arm64")
    else()
        message(FATAL_ERROR "Unsupported Android architecture: \${REX_TARGET_PROCESSOR}")
    endif()
    add_compile_definitions(REX_PLATFORM_ANDROID=1)
elseif(UNIX AND NOT APPLE)
    if(REX_TARGET_PROCESSOR MATCHES "AMD64|x86_64")''',
"Android platform selection")

edit("src/ui/CMakeLists.txt",
'''elseif(APPLE)
    set(REXUI_PLATFORM_SOURCES
        surface_mac.cpp
    )
else()
    set(REXUI_PLATFORM_SOURCES
        surface_gnulinux.cpp
    )
endif()''',
'''elseif(APPLE)
    set(REXUI_PLATFORM_SOURCES
        surface_mac.cpp
    )
elseif(ANDROID)
    set(REXUI_PLATFORM_SOURCES
        surface_android.cpp
    )
else()
    set(REXUI_PLATFORM_SOURCES
        surface_gnulinux.cpp
    )
endif()''',
"Android surface source selection")
edit("src/ui/CMakeLists.txt",
'''if(UNIX AND NOT APPLE)
    find_package(PkgConfig REQUIRED)''',
'''if(UNIX AND NOT APPLE AND NOT ANDROID)
    find_package(PkgConfig REQUIRED)''',
"skip desktop dependencies on Android")
edit("src/ui/window_sdl.cpp",
'''#if REX_PLATFORM_WIN32
#include <rex/ui/surface_win.h>
#elif REX_PLATFORM_MAC''',
'''#if REX_PLATFORM_WIN32
#include <rex/ui/surface_win.h>
#elif REX_PLATFORM_ANDROID
#include <rex/ui/surface_android.h>
#elif REX_PLATFORM_MAC''',
"Android surface include")
edit("src/ui/window_sdl.cpp",
'''#if REX_PLATFORM_WIN32
  SDL_PropertiesID props = SDL_GetWindowProperties(sdl_window_);''',
'''#if REX_PLATFORM_ANDROID
  if (allowed_types & Surface::kTypeFlag_AndroidNativeWindow) {
    SDL_PropertiesID props = SDL_GetWindowProperties(sdl_window_);
    auto* native_window = static_cast<ANativeWindow*>(
        SDL_GetPointerProperty(props, SDL_PROP_WINDOW_ANDROID_WINDOW_POINTER, nullptr));
    if (native_window) {
      return std::make_unique<AndroidNativeWindowSurface>(native_window, sdl_window_);
    }
  }
#elif REX_PLATFORM_WIN32
  SDL_PropertiesID props = SDL_GetWindowProperties(sdl_window_);''',
"Android native window surface creation")

header = root / "include/rex/ui/surface_android.h"
source = root / "src/ui/surface_android.cpp"
header.parent.mkdir(parents=True, exist_ok=True)
source.parent.mkdir(parents=True, exist_ok=True)
if not header.exists():
    header.write_text("""#pragma once
#include <rex/ui/surface.h>
#include <android/native_window.h>
struct SDL_Window;
namespace rex::ui {
class AndroidNativeWindowSurface final : public Surface {
 public:
  AndroidNativeWindowSurface(ANativeWindow* window, SDL_Window* sdl_window)
      : window_(window), sdl_window_(sdl_window) {}
  TypeIndex GetType() const override { return kTypeIndex_AndroidNativeWindow; }
  ANativeWindow* window() const { return window_; }
 protected:
  bool GetSizeImpl(uint32_t& width_out, uint32_t& height_out) const override;
 private:
  ANativeWindow* window_;
  SDL_Window* sdl_window_;
};
}  // namespace rex::ui
""", encoding="utf-8")
if not source.exists():
    source.write_text("""#include <rex/ui/surface_android.h>
#include <SDL3/SDL.h>
namespace rex::ui {
bool AndroidNativeWindowSurface::GetSizeImpl(uint32_t& width_out, uint32_t& height_out) const {
  int width = 0;
  int height = 0;
  if (!sdl_window_ || !SDL_GetWindowSizeInPixels(sdl_window_, &width, &height) ||
      width <= 0 || height <= 0) {
    width_out = 0;
    height_out = 0;
    return false;
  }
  width_out = static_cast<uint32_t>(width);
  height_out = static_cast<uint32_t>(height);
  return true;
}
}  // namespace rex::ui
""", encoding="utf-8")

checks = {
    root / "CMakeLists.txt": ["set(REX_PLATFORM \\"android-arm64\\")", "REX_PLATFORM_ANDROID=1"],
    root / "src/ui/CMakeLists.txt": ["surface_android.cpp", "NOT ANDROID"],
    root / "src/ui/window_sdl.cpp": ["SDL_PROP_WINDOW_ANDROID_WINDOW_POINTER", "AndroidNativeWindowSurface"],
    header: ["class AndroidNativeWindowSurface", "ANativeWindow* window()"],
    source: ["AndroidNativeWindowSurface::GetSizeImpl"],
}
for path, needles in checks.items():
    text = path.read_text(encoding="utf-8")
    missing = [n for n in needles if n not in text]
    if missing:
        raise SystemExit(f"[android-platform] sanity check failed in {path}: {missing}")
print("[android-platform] Android ARM64 platform selection and SDL/Vulkan surface patch: OK")
