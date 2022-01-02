using CSharp.Models;

namespace CSharp;

public static class Constants
{
    public static readonly byte[] QOI_END_MARKER = new[] { 0, 0, 0, 0, 0, 0, 0, 1 }
                                            .Select(x => (byte)x).ToArray();

    public const uint QOI_MAGIC_BYTES = 0x716f6966; // qoif
    public const byte QOI_HEADER_SIZE = 14;
    public const byte QOI_OP_INDEX = 0x00; // 00xxxxxx
    public const byte QOI_OP_DIFF  = 0x40; // 01xxxxxx
    public const byte QOI_OP_LUMA  = 0x80; // 10xxxxxx
    public const byte QOI_OP_RUN   = 0xc0; // 11xxxxxx
    public const byte QOI_OP_RGB   = 0xfe; // 11111110
    public const byte QOI_OP_RGBA  = 0xff; // 11111111

    public static readonly Color FirstColor = new(0, 0, 0, 255);
}
