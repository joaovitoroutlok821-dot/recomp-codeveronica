#!/usr/bin/env python3
"""Patch the pinned ReXGlue Android API-level query to use the NDK API."""
from pathlib import Path
import sys

def die(message):
    raise SystemExit("[android-api-level] ERROR: " + message)

if len(sys.argv) != 2:
    die("usage: ensure-rexglue-android-api-level.py <rexglue-sdk-root>")
p = Path(sys.argv[1]).resolve() / "src/core/memory_posix.cpp"
if not p.is_file():
    die(f"missing {p}")
s = p.read_text(encoding="utf-8")
old = "rex::GetAndroidApiLevel()"
new = "android_get_device_api_level()"
if old in s:
    s = s.replace(old, new)
if "#include <android/api-level.h>" not in s:
    anchor = "#if REX_PLATFORM_ANDROID\n"
    if anchor not in s:
        die("could not locate Android conditional include block")
    s = s.replace(anchor, anchor + "#include <android/api-level.h>\n", 1)
if old in s:
    die("unsupported API-level call remains")
p.write_text(s, encoding="utf-8")
print("[android-api-level] using NDK android_get_device_api_level()")
