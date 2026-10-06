from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class ShotScale(str, Enum):
    DETAIL = "detail"
    CLOSE_UP = "close_up"
    PORTRAIT = "portrait"
    MEDIUM = "medium"
    WIDE = "wide"
    DISTANT = "distant"


@dataclass(frozen=True, slots=True)
class Shot:
    scale: ShotScale = ShotScale.PORTRAIT
    fill_ratio: float | None = None

    def __post_init__(self) -> None:
        if self.fill_ratio is not None and not 0 < self.fill_ratio <= 1:
            raise ValueError("fill_ratio must be within (0,1]")
