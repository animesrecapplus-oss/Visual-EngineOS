import math  # LASH-CON: reject non-finite authored numeric state without coercion.
from dataclasses import dataclass
from numbers import Integral, Real  # LASH-CON: preserve numeric type semantics and reject bools.

from ..contracts.types import LashForm, LashStyle, LowerLashStyle
from ..contracts.validation import _color

@dataclass(frozen=True, slots=True)
class LashSpec:
    enabled: bool = True
    density: float = 0.82
    length: float = 0.07
    thickness: float = 0.020
    curvature: float = 0.5
    color: str = "#000000"
    count: int = 18
    style: LashStyle = "natural"
    spacing_jitter: float = 0.0
    outer_flare: float = 0.35
    inner_length_factor: float = 0.35
    upward_bias: float = 0.15
    taper: float = 0.25
    form: LashForm = "line"

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise TypeError("lash enabled must be bool")
        real_fields = (
            self.density, self.length, self.thickness, self.curvature, self.spacing_jitter,
            self.outer_flare, self.inner_length_factor, self.upward_bias, self.taper,
        )
        if any(isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value) for value in real_fields):
            raise ValueError("lash values must be finite numeric values")
        if isinstance(self.count, bool) or not isinstance(self.count, Integral):
            raise ValueError("lash count must be an integer")
        if (not 0 <= self.density <= 1 or self.length < 0 or self.thickness < 0 or self.count < 0
                or self.spacing_jitter < 0 or not 0 <= self.outer_flare <= 1
                or not 0 <= self.inner_length_factor <= 1 or not 0 <= self.upward_bias <= 1
                or not 0 <= self.taper <= 1):
            raise ValueError("invalid lashes")
        _color(self.color, "lash color")
        if self.style not in {"natural", "anime", "spiky", "ornate"}:
            raise ValueError("unknown lash style")
        if self.form not in {"line", "tapered", "clustered", "disheveled"}:
            raise ValueError("unknown lash form")


@dataclass(frozen=True, slots=True)
class LowerLashSpec:
    """Subordinate lower-lash system. Defaults are deliberately lighter and sparser."""
    enabled: bool = True
    density: float = 0.12
    length: float = 0.025
    thickness: float = 0.004
    curvature: float = 0.25
    color: str = "#666666"
    opacity: float = 0.34
    count: int = 7
    style: LowerLashStyle = "natural"
    outer_flare: float = 0.22
    downward_bias: float = 0.10
    taper: float = 0.45
    form: LashForm = "line"

    def __post_init__(self) -> None:
        if not isinstance(self.enabled, bool):
            raise TypeError("lower lash enabled must be bool")
        real_fields = (
            self.density, self.length, self.thickness, self.curvature, self.opacity,
            self.outer_flare, self.downward_bias, self.taper,
        )
        if any(isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value) for value in real_fields):
            raise ValueError("lower lash values must be finite numeric values")
        if isinstance(self.count, bool) or not isinstance(self.count, Integral):
            raise ValueError("lower lash count must be an integer")
        if (not 0 <= self.density <= 1 or self.length < 0 or self.thickness < 0
                or not 0 <= self.opacity <= 1 or self.count < 0
                or not 0 <= self.outer_flare <= 1 or not 0 <= self.downward_bias <= 1
                or not 0 <= self.taper <= 1 or self.curvature < 0):
            raise ValueError("invalid lower lashes")
        _color(self.color, "lower lash color")
        if self.style not in {"natural", "anime", "spiky"}:
            raise ValueError("unknown lower lash style")
        if self.form not in {"line", "tapered", "clustered", "disheveled"}:
            raise ValueError("unknown lower lash form")
