#!/usr/bin/env python3
"""THE MORNING LEDGER — NI24 entry program, Akun 14 (@namanyasiapa65237).

Copies the pre-rendered entry.png (drawn in code by compose.py in this
same repository, during this same session) to the output directory.
Standard library only; no network; deterministic: the same bytes out
on every run.
"""
import hashlib
import os
import shutil
import struct
import sys

ENTRY = "entry.png"
MAX_BYTES = 1048576
WANT_W = 1024
WANT_H = 1024


def png_size(path):
    """Read width/height straight from the PNG IHDR header."""
    with open(path, "rb") as f:
        head = f.read(33)
    if len(head) < 33 or head[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("entry.png is not a PNG file")
    if head[12:16] != b"IHDR":
        raise ValueError("entry.png has no IHDR chunk where expected")
    width, height = struct.unpack(">II", head[16:24])
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    src = os.path.join(here, ENTRY)
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    os.makedirs(out_dir, exist_ok=True)
    dst = os.path.join(out_dir, ENTRY)

    size = os.path.getsize(src)
    if size > MAX_BYTES:
        print(f"gate: entry.png is {size} bytes, over the 1 MiB cap", file=sys.stderr)
        return 1
    width, height = png_size(src)
    if (width, height) != (WANT_W, WANT_H):
        print(f"gate: entry.png is {width}x{height}, must be 1024x1024", file=sys.stderr)
        return 1

    shutil.copyfile(src, dst)
    # Prove the copy is exact: same bytes in, same bytes out, every run.
    digest_src = hashlib.sha256(open(src, "rb").read()).hexdigest()
    digest_dst = hashlib.sha256(open(dst, "rb").read()).hexdigest()
    if digest_src != digest_dst:
        print("gate: copied bytes differ from entry.png", file=sys.stderr)
        return 1
    print(f"wrote {dst} ({size} bytes, {width}x{height}, sha256 {digest_src[:16]}...)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
