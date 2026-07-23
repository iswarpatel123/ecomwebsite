"""Tiny dependency-free RGBA PNG reader/writer for verification artifacts.

Playwright emits ordinary 8-bit PNGs. Supporting the common non-interlaced
colour types here keeps screenshot comparison usable without Pillow or a paid
visual-testing service. Unsupported PNG variants fail with a useful message.
"""

from __future__ import annotations

import struct
import zlib
from pathlib import Path


PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def _paeth(a: int, b: int, c: int) -> int:
    p = a + b - c
    pa, pb, pc = abs(p - a), abs(p - b), abs(p - c)
    return a if pa <= pb and pa <= pc else b if pb <= pc else c


def read_png(path: str | Path) -> tuple[int, int, bytes]:
    data = Path(path).read_bytes()
    if not data.startswith(PNG_SIGNATURE):
        raise ValueError(f"Not a PNG: {path}")
    pos = len(PNG_SIGNATURE)
    width = height = bit_depth = color_type = interlace = None
    chunks: list[bytes] = []
    while pos < len(data):
        if pos + 12 > len(data):
            raise ValueError(f"Truncated PNG: {path}")
        length = struct.unpack(">I", data[pos : pos + 4])[0]
        kind = data[pos + 4 : pos + 8]
        payload_start, payload_end = pos + 8, pos + 8 + length
        payload = data[payload_start:payload_end]
        pos = payload_end + 4
        if kind == b"IHDR":
            width, height, bit_depth, color_type, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload)
            if compression != 0 or filtering != 0 or interlace != 0:
                raise ValueError("Only non-interlaced PNGs with standard compression are supported")
        elif kind == b"IDAT":
            chunks.append(payload)
        elif kind == b"IEND":
            break
    if width is None or height is None or bit_depth != 8 or color_type not in (0, 2, 4, 6):
        raise ValueError(f"Unsupported PNG format in {path}; expected 8-bit PNG")
    raw = zlib.decompress(b"".join(chunks))
    channels = {0: 1, 2: 3, 4: 2, 6: 4}[color_type]
    stride = width * channels
    expected = height * (stride + 1)
    if len(raw) != expected:
        raise ValueError(f"Invalid PNG scanline length in {path}")
    rows: list[bytes] = []
    offset = 0
    previous = bytes(stride)
    for _ in range(height):
        filter_type = raw[offset]
        encoded = raw[offset + 1 : offset + 1 + stride]
        offset += stride + 1
        row = bytearray(stride)
        for i, value in enumerate(encoded):
            left = row[i - channels] if i >= channels else 0
            above = previous[i]
            upper_left = previous[i - channels] if i >= channels else 0
            if filter_type == 0:
                result = value
            elif filter_type == 1:
                result = (value + left) & 255
            elif filter_type == 2:
                result = (value + above) & 255
            elif filter_type == 3:
                result = (value + ((left + above) // 2)) & 255
            elif filter_type == 4:
                result = (value + _paeth(left, above, upper_left)) & 255
            else:
                raise ValueError(f"Unsupported PNG filter {filter_type}")
            row[i] = result
        rows.append(bytes(row))
        previous = bytes(row)

    rgba = bytearray(width * height * 4)
    out = 0
    for row in rows:
        for i in range(width):
            pixel = row[i * channels : (i + 1) * channels]
            if color_type == 0:
                rgba[out : out + 4] = bytes((pixel[0], pixel[0], pixel[0], 255))
            elif color_type == 2:
                rgba[out : out + 4] = bytes((*pixel, 255))
            elif color_type == 4:
                rgba[out : out + 4] = bytes((pixel[0], pixel[0], pixel[0], pixel[1]))
            else:
                rgba[out : out + 4] = pixel
            out += 4
    return width, height, bytes(rgba)


def _chunk(kind: bytes, payload: bytes) -> bytes:
    return struct.pack(">I", len(payload)) + kind + payload + struct.pack(">I", zlib.crc32(kind + payload) & 0xFFFFFFFF)


def write_png(path: str | Path, width: int, height: int, rgba: bytes) -> None:
    if len(rgba) != width * height * 4:
        raise ValueError("RGBA buffer does not match PNG dimensions")
    scanlines = b"".join(b"\x00" + rgba[y * width * 4 : (y + 1) * width * 4] for y in range(height))
    payload = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)
    result = PNG_SIGNATURE + _chunk(b"IHDR", payload) + _chunk(b"IDAT", zlib.compress(scanlines, 6)) + _chunk(b"IEND", b"")
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_bytes(result)
