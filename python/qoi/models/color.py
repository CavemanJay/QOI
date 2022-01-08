from dataclasses import dataclass
from typing import Union


@dataclass
class Color:
    r: int
    g: int
    b: int
    a: Union[int, None] = None

    @property
    def index(self) -> int:
        return (self.r * 3 + self.g * 5 + self.b * 7 + self.a * 11) % 64

    def __sub__(self, prev: "Color") -> "ColorDiff":
        return ColorDiff(
            self.r - prev.r, self.g - prev.g, self.b - prev.b, self.a - prev.a
        )


class ColorDiff(Color):
    pass
