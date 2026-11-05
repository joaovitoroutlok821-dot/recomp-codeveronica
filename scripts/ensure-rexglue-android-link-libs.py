#!/usr/bin/env python3
"""Remove Linux-only pthread/rt link flags from ReXGlue's Android target."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: ensure-rexglue-android-link-libs.py /path/to/rexglue-sdk")

root = Path(sys.argv[1]).resolve()
cmake = root / "src/core/CMakeLists.txt"
if not cmake.is_file():
    raise SystemExit(f"[android-link-libs] missing {cmake}")

s = cmake.read_text(encoding="utf-8")
old = """if(APPLE)
    target_link_libraries(rexcore PRIVATE pthread)
elseif(UNIX)
    target_link_libraries(rexcore PRIVATE pthread rt dl)
endif()"""
new = """if(APPLE)
    target_link_libraries(rexcore PRIVATE pthread)
elseif(ANDROID)
    # Android's Bionic libc provides pthread APIs; librt is not available.
    # Keep libdl for dlopen/dlsym users in the POSIX runtime.
    target_link_libraries(rexcore PRIVATE dl)
elseif(UNIX)
    target_link_libraries(rexcore PRIVATE pthread rt dl)
endif()"""

if new not in s:
    if s.count(old) != 1:
        raise SystemExit("[android-link-libs] expected POSIX link block not found uniquely")
    s = s.replace(old, new, 1)
    cmake.write_text(s, encoding="utf-8")

check = cmake.read_text(encoding="utf-8")
if new not in check:
    raise SystemExit("[android-link-libs] patch verification failed")
print("[android-link-libs] Android links dl only; Linux pthread/rt flags preserved: OK")
