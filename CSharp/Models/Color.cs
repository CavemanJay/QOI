namespace CSharp.Models;

public record struct Color(int r, int g, int b, int a)
{
    private byte? colorIndex = null;
    public byte ColorIndex
    {
        get
        {
            if (colorIndex.HasValue) return colorIndex.Value;
            var hash = (byte)((r * 3 + g * 5 + b * 7 + a * 11) % 64);
            colorIndex = hash;
            return hash;
        }
    }

    public Color Diff(Color other)
    {
        return new(this.r - other.r, this.g - other.g, this.b - other.b, this.a - other.a);
    }

    public bool ColorEquals(Color other)
    {
        return
             this.r == other.r
             && this.g == other.g
             && this.b == other.b
             && this.a == other.a;
    }

}
