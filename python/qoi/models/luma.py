from dataclasses import dataclass

from qoi.models.color import ColorDiff


@dataclass(init=False)
class LumaDiff:
    green: int
    dr_dg: int
    db_dg: int

    def __init__(self, diff: ColorDiff) -> None:
        self.green = diff.g
        self.dr_dg = diff.r - diff.g
        self.db_dg = diff.b - diff.g
