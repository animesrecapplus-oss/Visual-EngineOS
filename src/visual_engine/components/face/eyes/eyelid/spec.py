from dataclasses import dataclass
import math
from numbers import Real

from ..contracts.types import ContourStyle
from ..contracts.validation import _color

@dataclass(frozen=True, slots=True)
class EyelidAppearance:
    """Appearance contract for mandatory eyelid margins and visible lid folds.

    The aperture boundary is the anatomical lid margin. The crease is a separate
    visible fold so an eye cannot silently become a sclera shape with lashes.
    """
    upper_enabled: bool = True
    lower_enabled: bool = True
    upper_color: str | None = None
    lower_color: str | None = None
    upper_width: float = 0.018
    lower_width: float = 0.012
    upper_opacity: float = 1.0
    lower_opacity: float = 1.0
    upper_style: ContourStyle | None = None
    lower_style: ContourStyle | None = None
    upper_crease_enabled: bool = True
    lower_crease_enabled: bool = True
    crease_color: str = "#000000"
    upper_crease_offset: float = 0.11
    lower_crease_offset: float = 0.075
    upper_crease_length: float = 0.82
    lower_crease_length: float = 0.62
    upper_crease_width: float = 0.010
    lower_crease_width: float = 0.006
    upper_crease_opacity: float = 0.48
    lower_crease_opacity: float = 0.22

    def __post_init__(self) -> None:
        # Local input invariant: boolean controls are actual booleans; numeric
        # appearance controls are finite real values before range checks.
        bool_fields = (
            self.upper_enabled, self.lower_enabled,
            self.upper_crease_enabled, self.lower_crease_enabled,
        )
        if any(not isinstance(value, bool) for value in bool_fields):
            raise TypeError("eyelid enabled fields must be bool")
        real_fields = (
            self.upper_width, self.lower_width, self.upper_opacity, self.lower_opacity,
            self.upper_crease_offset, self.lower_crease_offset,
            self.upper_crease_length, self.lower_crease_length,
            self.upper_crease_width, self.lower_crease_width,
            self.upper_crease_opacity, self.lower_crease_opacity,
        )
        for value in real_fields:
            if isinstance(value, bool) or not isinstance(value, Real):
                raise ValueError("eyelid appearance values must be finite numeric values")
            try:
                finite = math.isfinite(value)
            except OverflowError:
                finite = False
            if not finite:
                raise ValueError("eyelid appearance values must be finite numeric values")
        if (self.upper_width < 0 or self.lower_width < 0
                or not 0 <= self.upper_opacity <= 1 or not 0 <= self.lower_opacity <= 1
                or self.upper_crease_offset < 0 or self.lower_crease_offset < 0
                or not 0 < self.upper_crease_length <= 1 or not 0 < self.lower_crease_length <= 1
                or self.upper_crease_width < 0 or self.lower_crease_width < 0
                or not 0 <= self.upper_crease_opacity <= 1 or not 0 <= self.lower_crease_opacity <= 1):
            raise ValueError("invalid eyelid appearance")
        _color(self.crease_color, "eyelid crease color")
        if self.upper_color is not None:
            _color(self.upper_color, "upper eyelid color")
        if self.lower_color is not None:
            _color(self.lower_color, "lower eyelid color")
