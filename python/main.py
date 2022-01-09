import itertools
from os import PathLike
import struct
from typing import List

from qoi.constants import *
from qoi.exceptions import QoiHeaderError
from qoi.models import Color
from qoi.models.luma import LumaDiff
import qoi.operations as ops


with open("assets/monument.bin", "rb") as f:
    input_bytes = f.read()

# with open("assets/monument.qoi", "rb") as f:
#     reference = f.read(14)

color_channels = 4
# TODO: Use pure generators rather than creating an entire list
input_pixels = [
    Color(*input_bytes[i : i + color_channels])
    for i in range(0, len(input_bytes), color_channels)
]

image_width = 735
image_height = 588


def get_run_length(pixels: List[Color], prev_color: Color, index: int):
    i = index
    c = 0
    while True:
        if pixels[i] == prev_color:
            i += 1
            c += 1
        else:
            return c


def decode(file_path: PathLike):
    with open(file_path, "rb") as f:
        (
            magic_bytes,
            width,
            height,
            color_channels,
            color_space,
        ) = QOI_HEADER_STRUCT.unpack(f.read(QOI_HEADER_STRUCT.size))

        if magic_bytes != QOI_MAGIC_BYTES:
            raise QoiHeaderError(
                f"Invalid file header. Expected {QOI_MAGIC_BYTES} but got {magic_bytes}"
            )
        prev_color = QOI_FIRST_COLOR
        for byte in f.read(1):
            if byte == QOI_OP_RGB:
                color = Color(*struct.unpack("BBB", f.read(3)), prev_color.a)
                yield None
                continue

            if byte == QOI_OP_RGBA:
                color = Color(*struct.unpack("BBBB", f.read(4)))
                yield None
            print()
        print()


def encode():
    yield bytearray(
        QOI_HEADER_STRUCT.pack(QOI_MAGIC_BYTES, image_width, image_height, 4, 1)
    )
    seen_pixels = [Color(0, 0, 0, 0) for _ in range(64)]
    prev_color = QOI_FIRST_COLOR
    i = 0
    while i < len(input_pixels):
        # Run check
        run = get_run_length(input_pixels, prev_color, i)
        run_length = min(62, run)
        if run:
            i += run_length
            yield ops.Run(run_length)
            continue
        color = input_pixels[i]

        # Index check
        if seen_pixels[color.index] == color:
            i += 1
            prev_color = color
            yield ops.Index(color.index)
            continue

        seen_pixels[color.index] = color
        # Alpha equality check
        if color.a != prev_color.a:
            i += 1
            prev_color = color
            yield ops.Rgba(color)
            continue

        # Diff check
        diff = color - prev_color
        if (
            diff.r in QOI_DIFF_RANGE
            and diff.g in QOI_DIFF_RANGE
            and diff.b in QOI_DIFF_RANGE
        ):
            i += 1
            prev_color = color
            yield ops.Diff(diff)
            continue

        # Luma check
        luma = LumaDiff(diff)
        if (
            luma.green in QOI_LUMA_GREEN_RANGE
            and luma.dr_dg in QOI_LUMA_RB_RANGE
            and luma.db_dg in QOI_LUMA_RB_RANGE
        ):
            i += 1
            prev_color = color
            yield ops.Luma(luma)
            continue

        i += 1
        prev_color = color
        yield ops.Rgb(color)

    yield QOI_END_MARKER


# with open("output.qoi", "wb") as f:
#     for bytes in encode():
#         f.write(bytes)

decoded = list(decode("output.qoi"))
# print()
