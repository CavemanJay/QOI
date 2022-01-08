import struct
from .models import Color

QOI_MAGIC_BYTES = b"qoif"

QOI_OP_RUN = 0b11000000
QOI_OP_INDEX = 0b00000000
QOI_OP_DIFF = 0b01000000
QOI_OP_LUMA = 0b10000000
QOI_OP_RGB = 0b11111110
QOI_OP_RGBA = 0b11111111

QOI_RUN_BIAS = -1
QOI_DIFF_BIAS = 2
QOI_DIFF_RANGE=list(range(-2,2))

QOI_LUMA_GREEN_BIAS = 32
QOI_LUMA_RB_BIAS = 8
QOI_LUMA_GREEN_RANGE = list(range(-32, 32))
QOI_LUMA_RB_RANGE = list(range(-8, 8))

QOI_FIRST_COLOR = Color(0, 0, 0, 255)

QOI_HEADER_STRUCT = struct.Struct(">" "4s" "I" "I" "B" "B")  # big-endian

QOI_END_MARKER = bytearray([0 for _ in range(7)] + [1])
