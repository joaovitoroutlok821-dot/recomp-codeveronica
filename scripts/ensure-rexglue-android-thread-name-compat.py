#!/usr/bin/env python3
"""Remove the obsolete pre-API-26 thread-name call from the Android SDK build."""
from pathlib import Path
import re
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: ensure-rexglue-android-thread-name-compat.py /path/to/rexglue-sdk")

src = Path(sys.argv[1]).resolve() / "src/core/threading_posix.cpp"
if not src.is_file():
    raise SystemExit(f"[android-thread-name] missing source: {src}")

s = src.read_text(encoding="utf-8")
before = s

# The target is Android API 26+, where pthread_setname_np is available.
# Remove the unavailable header and only the call to the old compatibility
# helper; leave its unused class method/fields alone to avoid brittle edits.
s = s.replace("#include <rex/main_android.h>\n", "")
s, removed_calls = re.subn(
    r"^[ \t]*.*\.SetAndroidPreApi26Name\(name\);[ \t]*\n",
    "",
    s,
    flags=re.MULTILINE,
)

if "#include <rex/main_android.h>" in s:
    raise SystemExit("[android-thread-name] obsolete header reference remains")
if re.search(r"^[ \t]*.*\.SetAndroidPreApi26Name\(name\);", s, flags=re.MULTILINE):
    raise SystemExit("[android-thread-name] obsolete helper call remains")
if "pthread_setname_np(thread_, std::string(name).c_str());" not in s:
    raise SystemExit("[android-thread-name] expected Android thread naming call missing")

if s == before:
    print("[android-thread-name] patch already applied")
    raise SystemExit(0)
if removed_calls == 0:
    raise SystemExit("[android-thread-name] expected obsolete helper call was not found")

src.write_text(s, encoding="utf-8")
print("[android-thread-name] removed obsolete pre-API-26 helper call")
