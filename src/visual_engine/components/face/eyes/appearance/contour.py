from dataclasses import dataclass
from typing import Literal

from ..contracts.types import ContourStyle
from ..contracts.validation import _color, _finite

@dataclass(frozen=True, slots=True)
class ContourSpec:
    """Per-component contour contract. Defaults follow the engine's human/anime baseline."""
    color: str = "#000000"
    secondary_color: str | None = None
    width: float = 0.018
    style: ContourStyle = "solid"
    upper_width_factor: float = 1.0
    lower_width_factor: float = 1.0
    opacity: float = 1.0
    cap: Literal["butt", "round", "square"] = "round"
    join: Literal["miter", "round", "bevel"] = "round"

    def __post_init__(self) -> None:
        if not _finite((self.width, self.upper_width_factor, self.lower_width_factor, self.opacity)):
            raise ValueError("contour values must be finite")
        if self.width < 0 or self.upper_width_factor < 0 or self.lower_width_factor < 0 or not 0 <= self.opacity <= 1:
            raise ValueError("invalid contour")
        if self.style not in {"solid", "dashed", "double", "tapered"}:
            raise ValueError("unknown contour style")
        _color(self.color, "contour color")
        if self.secondary_color is not None:
            _color(self.secondary_color, "contour secondary color")
