import heartrate
import struct
from typing import Iterable, List

from qoi.constants import *
from qoi.models import Color
from qoi.models.luma import LumaDiff
import qoi.operations as ops

def to_int32_bytes(value: int) -> bytes:
    return struct.pack("I", value)


def to_byte(value: int) -> bytes:
    return struct.pack("B", value)


with open("assets/monument.bin", "rb") as f:
    input_bytes = f.read()

# with open("assets/monument.qoi", "rb") as f:
#     reference = f.read(14)

color_channels = 4
# TODO: Use pure generators rather than creating an entire list
input_pixels = list(
    Color(*input_bytes[i : i + color_channels])
    for i in range(0, len(input_bytes), color_channels)
)

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


def get_run(colors: Iterable[Color], previous_color: Color):
    count = 0
    color = next(colors)
    while count < QOI_RUN_MAX:
        if color == previous_color:
            count += 1
            color = next(colors)
        else:
            return count, color

    return count, color


@profile
def encode():
    yield QOI_HEADER_STRUCT.pack(QOI_MAGIC_BYTES, image_width, image_height, 4, 1)
    seen_pixels = [Color(0, 0, 0, 0) for _ in range(64)]
    prev_color = QOI_FIRST_COLOR
    i = 0
    while i < len(input_pixels):
    # while True:
        # Run check
        run = get_run_length(input_pixels, prev_color, i)
        # run, color = get_run(input_pixels, prev_color)

        run_length = min(QOI_RUN_MAX, run)
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


with open("output.qoi", "wb") as f:
    for bytes in encode():
        f.write(bytes)

# print()
