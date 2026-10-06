import math
from dataclasses import dataclass
from numbers import Integral, Real  # IRIS-CON: reject coercive strings/bools at the local boundary.

from ..contracts.validation import _color
from ..contracts.types import IrisShape

@dataclass(frozen=True, slots=True)
class IrisSpec:
    shape: IrisShape = "circle"
    color: str = "#3d7aa6"
    inner_color: str | None = None
    outer_color: str | None = None
    pattern: str = "none"
    ring_count: int = 0
    glow: float = 0.0
    opacity: float = 1.0
    pattern_strength: float = 0.0
    pattern_count: int = 12
    outline_color: str = "#000000"
    outline_width: float = 0.018

    def __post_init__(self) -> None:
        integer_fields = (self.ring_count, self.pattern_count)  # INV-IRIS-001: loop bounds stay true integers.
        real_fields = (self.glow, self.opacity, self.pattern_strength, self.outline_width)  # INV-IRIS-003: finite real state.
        # Counts feed renderer range(...) calls; reject permissive bool/fractional state before rendering.
        if any(isinstance(value, bool) or not isinstance(value, Integral) for value in integer_fields):
            raise ValueError("iris ring and pattern counts must be integers")
        if any(isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value) for value in real_fields):
            raise ValueError("iris numeric values must be finite numeric values")
        if self.ring_count < 0 or self.pattern_count < 1:
            raise ValueError("invalid iris counts")
        if not 0 <= self.glow <= 1 or not 0 <= self.opacity <= 1:
            raise ValueError("invalid iris opacity/glow")
        if not 0 <= self.pattern_strength <= 1 or self.outline_width < 0:
            raise ValueError("invalid iris pattern")
        _color(self.color, "iris color")
        _color(self.outline_color, "iris outline color")
        if self.inner_color is not None:
            _color(self.inner_color, "iris inner_color")
        if self.outer_color is not None:
            _color(self.outer_color, "iris outer_color")
