#!/usr/bin/env python3
"""Carrier for THE FIRST EDITION (News Image, 24 November 2026).

Stdlib-only: reads entry.png from this directory, verifies the bounty
gates (PNG, exactly 1024x1024, at most 1 MiB), then writes the image
bytes to stdout unchanged.
"""
import os
import struct
import sys

MAX_BYTES = 1024 * 1024
EXPECTED_W = 1024
EXPECTED_H = 1024


def png_dimensions(data):
    if len(data) < 24 or data[:8] != b"\x89PNG\r\n\x1a\n":
        raise ValueError("entry.png is not a PNG file")
    if data[12:16] != b"IHDR":
        raise ValueError("entry.png is missing its IHDR chunk")
    width, height = struct.unpack(">II", data[16:24])
    return width, height


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(here, "entry.png")
    with open(path, "rb") as fh:
        data = fh.read()
    if len(data) > MAX_BYTES:
        raise ValueError("entry.png exceeds the 1 MiB gate: %d bytes" % len(data))
    width, height = png_dimensions(data)
    if (width, height) != (EXPECTED_W, EXPECTED_H):
        raise ValueError(
            "entry.png must be %dx%d, got %dx%d"
            % (EXPECTED_W, EXPECTED_H, width, height)
        )
    sys.stdout.buffer.write(data)
    sys.stdout.buffer.flush()
    return 0


if __name__ == "__main__":
    sys.exit(main())
