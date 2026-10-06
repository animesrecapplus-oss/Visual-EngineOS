import math
from dataclasses import dataclass
from numbers import Real
from typing import Literal

from ..contracts.validation import _color

@dataclass(frozen=True, slots=True)
class ReflectionMark:
    """Structured vector reflection/highlight; safe alternative to raw SVG markup."""
    shape: Literal["circle", "ellipse", "diamond", "streak"] = "circle"
    x: float = 0.0
    y: float = 0.0
    width: float = 0.10
    height: float = 0.10
    color: str = "#ffffff"
    opacity: float = 0.9
    rotation_deg: float = 0.0

    def __post_init__(self) -> None:
        if self.shape not in ("circle", "ellipse", "diamond", "streak"):
            raise ValueError("unknown reflection mark shape")
        numeric = (self.x, self.y, self.width, self.height, self.opacity, self.rotation_deg)
        if any(isinstance(value, bool) or not isinstance(value, Real) for value in numeric):
            raise ValueError("reflection values must be finite numeric values")
        for value in numeric:
            try:
                finite = math.isfinite(value)
            except (OverflowError, TypeError):
                finite = False
            if not finite:
                raise ValueError("reflection values must be finite numeric values")
        if self.width < 0 or self.height < 0 or not 0 <= self.opacity <= 1:
            raise ValueError("invalid reflection mark")
        _color(self.color, "reflection mark color")
