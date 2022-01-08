import struct
from qoi.models import Color, LumaDiff, ColorDiff
import qoi.constants as const


def Run(count: int):
    x= struct.pack("B", const.QOI_OP_RUN | (count + const.QOI_RUN_BIAS))
    return x


def Index(index: int):
    x= struct.pack("B", const.QOI_OP_INDEX | index)
    return x


def Diff(diff: ColorDiff):
    shifted_r = (diff.r + const.QOI_DIFF_BIAS) << 4
    shifted_g = (diff.g + const.QOI_DIFF_BIAS) << 2
    shifted_b = (diff.b + const.QOI_DIFF_BIAS) << 0
    x= struct.pack("B", const.QOI_OP_DIFF | shifted_r | shifted_g | shifted_b)
    return x


def Luma(luma: LumaDiff):
    byte_1 = const.QOI_OP_LUMA | (luma.green + const.QOI_LUMA_GREEN_BIAS)
    byte_2 = ((luma.dr_dg + const.QOI_LUMA_RB_BIAS) << 4) | (
        luma.db_dg + const.QOI_LUMA_RB_BIAS
    )
    x=  struct.pack("BB", byte_1, byte_2)
    return x


def Rgb(color: Color):
    x= struct.pack("BBBB", const.QOI_OP_RGB, color.r, color.g, color.b)
    return x


def Rgba(color: Color):
    x= struct.pack("BBBBB", const.QOI_OP_RGBA, color.r, color.g, color.b, color.a)
    return x
