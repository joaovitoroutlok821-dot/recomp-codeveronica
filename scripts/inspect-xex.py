#!/usr/bin/env python3
"""Non-decrypting sanity check for a locally supplied Xbox 360 XEX."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def ascii_strings(data: bytes, minimum: int = 6):
    pattern = rb"[\x20-\x7e]{%d,}" % minimum
    for match in re.finditer(pattern, data):
        yield match.start(), match.group().decode("ascii", "replace")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inspect a local XEX without decrypting or uploading it"
    )
    parser.add_argument("xex", nargs="?", default="game/Default.xex")
    args = parser.parse_args()
    path = Path(args.xex)
    if not path.is_file():
        print(f"ERROR: XEX not found: {path}", file=sys.stderr)
        return 2

    data = path.read_bytes()
    print(f"file:   {path}")
    print(f"size:   {len(data)} bytes")
    print(f"magic:  {data[:4]!r}")

    needles = ("Bio_cv.exe", "xboxkrnl.exe", "xam.xex")
    found = set()
    print("\ninteresting strings:")
    for offset, value in ascii_strings(data):
        if any(needle.lower() in value.lower() for needle in needles) and value not in found:
            print(f"  0x{offset:08X}: {value}")
            found.add(value)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
