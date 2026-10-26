#!/usr/bin/env python3
"""Use ReXGlue's portable C-locale float parser on Android libc++ too."""
from pathlib import Path
import sys

if len(sys.argv) != 2:
    raise SystemExit("usage: ensure-rexglue-android-float-from-chars.py /path/to/rexglue-sdk")
root = Path(sys.argv[1]).resolve()
path = root / "include/rex/string/numeric.h"
if not path.is_file():
    raise SystemExit(f"[android-float] missing file: {path}")
text = path.read_text(encoding="utf-8")
old = "#if REX_PLATFORM_MAC"
new = "#if REX_PLATFORM_MAC || REX_PLATFORM_ANDROID"
count = text.count(old)
if count == 0:
    if new not in text:
        raise SystemExit("[android-float] expected platform guards were not found")
else:
    text = text.replace(old, new)
    path.write_text(text, encoding="utf-8")
# Ensure both float parsing paths and the locale header are covered.
if text.count(new) < 3:
    raise SystemExit("[android-float] expected parser guards were not all patched")
print(f"[android-float] enabled portable float parsing for Android ({max(count, 0)} guards updated)")
