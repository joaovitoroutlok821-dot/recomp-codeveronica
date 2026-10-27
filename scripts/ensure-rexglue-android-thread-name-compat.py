#!/usr/bin/env python3
"""Remove an obsolete pre-API-26 thread-name helper from the Android SDK build."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: ensure-rexglue-android-thread-name-compat.py /path/to/rexglue-sdk")

src = Path(sys.argv[1]).resolve() / "src/core/threading_posix.cpp"
if not src.is_file():
    raise SystemExit(f"[android-thread-name] missing source: {src}")

s = src.read_text(encoding="utf-8")
before = s
include = "#include <rex/main_android.h>"
call = "    SetAndroidPreApi26Name(name);"

# The project targets Android API 26+, where pthread_setname_np is available.
# This helper/header exists only for older Android versions and is not present
# in the pinned upstream SDK. Keep the normal pthread_setname_np call intact.
s = s.replace(include + "\n", "")
s = s.replace(call + "\n", "")

if s == before:
    if include not in before and "SetAndroidPreApi26Name(name)" not in before:
        print("[android-thread-name] obsolete pre-API-26 helper already absent")
        raise SystemExit(0)
    raise SystemExit("[android-thread-name] no expected change was applied")

if include in s or "SetAndroidPreApi26Name(name)" in s:
    raise SystemExit("[android-thread-name] obsolete helper reference remains")

if "pthread_setname_np(thread_, std::string(name).c_str());" not in s:
    raise SystemExit("[android-thread-name] expected Android thread naming call missing")

src.write_text(s, encoding="utf-8")
print("[android-thread-name] removed unavailable pre-API-26 helper for API 26+ target")
