using CSharp.Models;
using System.Diagnostics;
using System.Linq;

namespace CSharp;

public class Encoder
{
    private readonly uint width;
    private readonly uint height;
    private readonly ColorChannels channels;
    private readonly ColorSpace colorSpace;
    private readonly string inputFilePath;

    private uint index = 0;
    private long lastPixel;
    private byte[] outputBuffer;

    public Encoder(uint width, uint height, ColorChannels channels,
        ColorSpace colorSpace, string filePath)
    {
        this.width = width;
        this.height = height;
        this.channels = channels;
        this.colorSpace = colorSpace;
        this.inputFilePath = filePath;
    }

    private void Write32(uint value)
    {
        outputBuffer[index++] = (byte)((value & 0xff000000) >> 24);
        outputBuffer[index++] = (byte)((value & 0x00ff0000) >> 16);
        outputBuffer[index++] = (byte)((value & 0x0000ff00) >> 8);
        outputBuffer[index++] = (byte)((value & 0x000000ff) >> 0);
    }

    private void WriteHeader()
    {
        Write32(Constants.QOI_MAGIC_BYTES);
        Write32(width);
        Write32(height);
        outputBuffer[index++] = (byte)channels;
        outputBuffer[index++] = (byte)colorSpace;
    }

    public byte[] Encode()
    {
        ReadOnlySpan<byte> inputBytes = InitializeOutputBuffer();
        var seenPixels = Enumerable.Repeat(new Color(0, 0, 0, 0), 64).ToArray();
        WriteHeader();
        byte run = 0;

        var prevColor = Constants.FirstColor;
        for (int offset = 0; offset <= lastPixel; offset += (byte)channels) 
        {
            var currentColor = new Color(
                inputBytes[offset + 0],
                inputBytes[offset + 1],
                inputBytes[offset + 2],
                (channels == ColorChannels.RGBA) ? inputBytes[offset + 3] : prevColor.a
                );

            if (currentColor.ColorEquals(prevColor))
            {
                run++;
                if (run == 62 || offset == lastPixel)
                {
                    outputBuffer[index++] = (byte)(Constants.QOI_OP_RUN | (run - 1));
                    run = 0;
                }
            }
            else
            {
                if (run > 0)
                {
                    outputBuffer[index++] = (byte)(Constants.QOI_OP_RUN | (run - 1));
                    run = 0;
                }

                if (currentColor.ColorEquals(seenPixels[currentColor.ColorIndex]))
                {
                    outputBuffer[index++] = (byte)(Constants.QOI_OP_INDEX | currentColor.ColorIndex);
                }
                else
                {
                    seenPixels[currentColor.ColorIndex] = currentColor;

                    var diff = currentColor.Diff(prevColor);
                    var dr_dg = diff.r - diff.g;
                    var db_dg = diff.b - diff.g;

                    if (diff.a == 0)
                    {
                        if ((diff.r >= -2 && diff.r <= 1) && (diff.g >= -2 && diff.g <= 1) && (diff.b >= -2 && diff.b <= 1))
                        {
                            outputBuffer[index++] = (
                              (byte)(Constants.QOI_OP_DIFF
                              | ((diff.r + 2) << 4)
                              | ((diff.g + 2) << 2)
                              | ((diff.b + 2) << 0))
                            );
                        }
                        else if ((diff.g >= -32 && diff.g <= 31) && (dr_dg >= -8 && dr_dg <= 7) && (db_dg >= -8 && db_dg <= 7))
                        {
                            outputBuffer[index++] = (byte)(Constants.QOI_OP_LUMA | (diff.g + 32));
                            outputBuffer[index++] = (byte)(((dr_dg + 8) << 4) | (db_dg + 8));
                        }
                        else
                        {
                            outputBuffer[index++] = Constants.QOI_OP_RGB;
                            outputBuffer[index++] = (byte)currentColor.r;
                            outputBuffer[index++] = (byte)currentColor.g;
                            outputBuffer[index++] = (byte)currentColor.b;
                        }
                    }
                    else
                    {
                        outputBuffer[index++] = Constants.QOI_OP_RGBA;
                        outputBuffer[index++] = (byte)currentColor.r;
                        outputBuffer[index++] = (byte)currentColor.g;
                        outputBuffer[index++] = (byte)currentColor.b;
                        outputBuffer[index++] = (byte)currentColor.a;
                    }
                }
            }
            prevColor = currentColor;
        }

        foreach (var b in Constants.QOI_END_MARKER)
        {
            outputBuffer[index++] = b;
        }

        return outputBuffer.Take((int)index).ToArray();
    }

    private byte[] InitializeOutputBuffer()
    {
        var inputBytes = File.ReadAllBytes(inputFilePath);
        var imageSize = inputBytes.Length;
        if (imageSize > int.MaxValue)
            throw new Exception("Cannot encode an image of this size at this time");

        this.lastPixel = imageSize - ((byte)channels);
        var maxSize = width * height * (((byte)channels) + 1) + Constants.QOI_HEADER_SIZE + Constants.QOI_END_MARKER.Length;
        this.outputBuffer = new byte[maxSize];

        return inputBytes;
    }
}
