import itertools
import struct
from typing import Any, Callable, List

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
# input_pixels2 = [
#     Color(*input_bytes[i : i + color_channels])
#     for i in range(0, len(input_bytes), color_channels)
# ]
input_pixels = [
    Color(*input_bytes[i : i + color_channels])
    for i in range(0, len(input_bytes), color_channels)
]

image_width = 735
image_height = 588


def takewhile_from_index(predicate: Callable, lst: List[Any], index: int = 0):
    i = index
    l = len(lst)
    while True:
        if predicate(lst[i]):
            yield lst[i]
            i+=1
        else:
            break


def encode():
    yield bytearray(QOI_HEADER_STRUCT.pack(QOI_MAGIC_BYTES, image_width, image_height, 4, 1))
    seen_pixels = [Color(0, 0, 0, 0) for _ in range(64)]
    prev_color = QOI_FIRST_COLOR
    # i = 0

    # def inc(amount=1):
    #     global input_pixels
    #     # global i
    #     # i += amount
    #     input_pixels = input_pixels[amount:]

    # while True:
    # while input_pixels:
    i = 0
    while i < len(input_pixels):
        # Run check
        # run = list(itertools.takewhile(lambda x: x == prev_color, input_pixels))
        run = list(takewhile_from_index(lambda x: x == prev_color, input_pixels, i))
        if run:
            run_length = len(run)
            i += run_length
            # inc(run_length)
            yield ops.Run(run_length)
            continue
        # color = next(input_pixels)
        color = input_pixels[i]

        # Index check
        if seen_pixels[color.index] == color:
            i += 1
            # inc()
            yield ops.Index(color.index)
            continue

        seen_pixels[color.index] = color
        # Alpha equality check
        if color.a != prev_color.a:
            # inc()
            i+=1
            yield ops.Rgba(color)
            continue

        # Diff check
        diff = color - prev_color
        if (
            diff.r in QOI_DIFF_RANGE
            and diff.g in QOI_DIFF_RANGE
            and diff.b in QOI_DIFF_RANGE
        ):
            # inc()
            i+=1
            yield ops.Diff(diff)
            continue

        # Luma check
        luma = LumaDiff(diff)
        if (
            luma.green in QOI_LUMA_GREEN_RANGE
            and luma.dr_dg in QOI_LUMA_RB_RANGE
            and luma.db_dg in QOI_LUMA_RB_RANGE
        ):
            # inc()
            i+=1
            yield ops.Luma(luma)
            continue

        i += 1
        # inc()
        yield ops.Rgb(color)
        prev_color = color

    yield QOI_END_MARKER


with open("output.qoi", "wb") as f:
    # header_bytes = QOI_HEADER_STRUCT.pack(
    #     QOI_MAGIC_BYTES, image_width, image_height, 4, 1
    # )
    # f.write(header_bytes)
    # # f.write(header_bytes)
    # f.write(QOI_END_MARKER)
    # bytes = list(encode())
    # result = bytearray()
    for bytes in encode():
        f.write(bytes)
        f.flush()
        print()
        # result+=byte

    # f.write(result)
    print()
# print()
