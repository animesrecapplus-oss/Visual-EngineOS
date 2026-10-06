from __future__ import annotations

from dataclasses import dataclass
import math

from ..contracts.validation import _color, _finite

@dataclass(frozen=True, slots=True)
class CaruncleSpec:
    """Optional medial caruncle appearance; it is not the canthus itself."""

    enabled: bool = True
    color: str = "#e8a17f"
    opacity: float = 0.58
    width: float = 0.035
    height: float = 0.065
    curvature: float = 0.65

    def __post_init__(self) -> None:
        if not _finite((self.opacity, self.width, self.height, self.curvature)):
            raise ValueError("caruncle values must be finite")
        if not 0 <= self.opacity <= 1 or self.width <= 0 or self.height <= 0 or not 0 <= self.curvature <= 1:
            raise ValueError("invalid caruncle specification")
        _color(self.color, "caruncle color")
