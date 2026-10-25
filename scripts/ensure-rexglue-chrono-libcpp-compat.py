#!/usr/bin/env python3
"""Enable ReXGlue's chrono clock_cast compatibility shim for libc++ hosts."""

from pathlib import Path
import sys


def main() -> int:
    if len(sys.argv) != 2:
        raise SystemExit("usage: ensure-rexglue-chrono-libcpp-compat.py <rexglue-sdk-root>")

    sdk = Path(sys.argv[1]).resolve()
    header = sdk / "include/rex/chrono/chrono.h"
    if not header.is_file():
        raise SystemExit(f"[chrono-libcpp] missing header: {header}")

    text = header.read_text(encoding="utf-8")
    old = "#ifdef __APPLE__\n// Apple libc++ does not expose clock_time_conversion or clock_cast."
    new = "#if defined(__APPLE__) || defined(_LIBCPP_VERSION)\n// Apple and upstream libc++ versions without clock_time_conversion/clock_cast need this shim."
    if old in text:
        text = text.replace(old, new, 1)
        header.write_text(text, encoding="utf-8")
        print("[chrono-libcpp] enabled clock_cast compatibility shim for libc++")
    elif new in text:
        print("[chrono-libcpp] libc++ clock_cast compatibility shim already enabled")
    else:
        raise SystemExit("[chrono-libcpp] could not locate the expected Apple chrono compatibility block")

    final = header.read_text(encoding="utf-8")
    if "#if defined(__APPLE__) || defined(_LIBCPP_VERSION)" not in final:
        raise SystemExit("[chrono-libcpp] sanity check failed")
    print("[chrono-libcpp] OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
