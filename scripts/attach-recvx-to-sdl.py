#!/usr/bin/env python3
"""Attach the ReXGlue title project to SDL's existing Android libmain target."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: attach-recvx-to-sdl.py /path/to/SDL/android-project")

android_project = Path(sys.argv[1]).resolve()
cmake = android_project / "app/jni/src/CMakeLists.txt"
if not cmake.is_file():
    raise SystemExit(f"[recvx-sdl] SDL Android source CMake file not found: {cmake}")

text = cmake.read_text(encoding="utf-8")
old = """add_library(main SHARED
    YourSourceHere.c
)
target_link_libraries(main PRIVATE SDL3::SDL3)
"""
new = """# ReXGlue attaches the title to this SDL-owned target. Do not create a
# second shared library named libmain.so.
add_library(main SHARED)
target_link_libraries(main PRIVATE SDL3::SDL3)

if(NOT RECVX_SOURCE_ROOT OR NOT IS_DIRECTORY "${RECVX_SOURCE_ROOT}")
    message(FATAL_ERROR "Set RECVX_SOURCE_ROOT to the private Resident Evil source tree")
endif()
add_subdirectory("${RECVX_SOURCE_ROOT}" "${CMAKE_CURRENT_BINARY_DIR}/recvx")
"""
if new not in text:
    if text.count(old) != 1:
        raise SystemExit("[recvx-sdl] expected the pinned SDL main target definition exactly once")
    text = text.replace(old, new, 1)
    cmake.write_text(text, encoding="utf-8")

check = cmake.read_text(encoding="utf-8")
for needle in ("add_library(main SHARED)", "target_link_libraries(main PRIVATE SDL3::SDL3)",
               'add_subdirectory("${RECVX_SOURCE_ROOT}"'):
    if needle not in check:
        raise SystemExit(f"[recvx-sdl] validation failed: missing {needle}")
if "YourSourceHere.c" in check:
    raise SystemExit("[recvx-sdl] SDL sample source still attached to main")
print("[recvx-sdl] SDL libmain target is ready for ReXGlue attachment")
