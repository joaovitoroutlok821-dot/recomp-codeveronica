#!/usr/bin/env python3
"""Patch ReXGlue POSIX threading for Android NDK compatibility."""
from pathlib import Path
import re
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: ensure-rexglue-android-thread-name-compat.py /path/to/rexglue-sdk")

src = Path(sys.argv[1]).resolve() / "src/core/threading_posix.cpp"
if not src.is_file():
    raise SystemExit(f"[android-thread-compat] missing source: {src}")

s = src.read_text(encoding="utf-8")
before = s

# Remove the obsolete pre-API-26 helper, unavailable in the Android NDK build.
s = s.replace("#include <rex/main_android.h>\n", "")
s = re.sub(
    r"^[ \t]*.*SetAndroidPreApi26Name\(name\);[ \t]*\n",
    "",
    s,
    flags=re.MULTILINE,
)

# Use the Android NDK API-level query instead of the SDK's legacy helper.
if "#include <android/api-level.h>" not in s:
    anchor = "#include <pthread.h>\n"
    if anchor not in s:
        raise SystemExit("[android-thread-compat] pthread include anchor missing")
    s = s.replace(
        anchor,
        anchor + "#if defined(__ANDROID__)\n#include <android/api-level.h>\n#endif\n",
        1,
    )
s = s.replace("rex::GetAndroidApiLevel()", "android_get_device_api_level()")

# PTHREAD_MUTEX_ROBUST / pthread_mutex_consistent are not exposed by this NDK
# configuration. Guard the robust-mutex blocks without relying on indentation.
s, robust_guards = re.subn(
    r"(?m)^([ \t]*)#if REX_PLATFORM_LINUX(?=\n[ \t]*(?:// Use robust mutexes so waits can recover if owner thread terminates\.|auto native_mutex = static_cast<pthread_mutex_t\*>|int lock_result = pthread_mutex_lock))",
    r"\1#if REX_PLATFORM_LINUX && !REX_PLATFORM_ANDROID",
    s,
)
if robust_guards < 3:
    raise SystemExit(
        f"[android-thread-compat] expected 3 robust-mutex guards, patched {robust_guards}"
    )

if "#include <rex/main_android.h>" in s:
    raise SystemExit("[android-thread-compat] obsolete header reference remains")
if "SetAndroidPreApi26Name(name);" in s:
    raise SystemExit("[android-thread-compat] obsolete helper call remains")
if "rex::GetAndroidApiLevel()" in s:
    raise SystemExit("[android-thread-compat] obsolete API-level helper remains")
if "pthread_setname_np(thread_, std::string(name).c_str());" not in s:
    raise SystemExit("[android-thread-compat] expected Android thread naming call missing")
if s == before:
    print("[android-thread-compat] patch already applied")
else:
    src.write_text(s, encoding="utf-8")
    print("[android-thread-compat] patched Android API-level and Linux-only robust mutex paths")
