from dataclasses import dataclass
import math
from numbers import Real

from ..contracts.types import BrowStyle
from ..contracts.validation import _color

@dataclass(frozen=True, slots=True)
class BrowSpec:
    enabled: bool = True
    shape: BrowStyle = "arched"
    length: float = 0.75
    thickness: float = 0.10
    density: float = 0.8
    angle_deg: float = 0.0
    x: float = 0.0
    y: float = -0.75
    color: str = "#000000"
    ornament: float = 0.0
    fade_at_inner: float = 0.0
    fade_at_outer: float = 0.0
    # V1.8 raises the default eye-to-brow clearance. This is a style/placement
    # default, not an anatomical constant; explicit authors can still override it.
    min_eye_gap: float = 0.45
    max_eye_gap: float = 0.90

    def __post_init__(self) -> None:
        # Local input invariant: booleans are strict and numeric values must be
        # finite Real values before any downstream arithmetic or SVG formatting.
        if not isinstance(self.enabled, bool):
            raise TypeError("eyebrow enabled must be bool")
        real_fields = (
            self.length, self.thickness, self.density, self.angle_deg, self.x, self.y,
            self.ornament, self.fade_at_inner, self.fade_at_outer, self.min_eye_gap, self.max_eye_gap,
        )
        for value in real_fields:
            if isinstance(value, bool) or not isinstance(value, Real):
                raise ValueError("eyebrow values must be finite numeric values")
            try:
                finite = math.isfinite(value)
            except OverflowError:
                finite = False
            if not finite:
                raise ValueError("eyebrow values must be finite numeric values")
        if self.length < 0 or self.thickness < 0 or not 0 <= self.density <= 1 or not 0 <= self.ornament <= 1:
            raise ValueError("invalid eyebrow")
        if self.min_eye_gap < 0 or self.max_eye_gap < self.min_eye_gap:
            raise ValueError("invalid eyebrow eye-gap bounds")
        if not 0 <= self.fade_at_inner <= 1 or not 0 <= self.fade_at_outer <= 1:
            raise ValueError("invalid eyebrow fade")
        _color(self.color, "eyebrow color")
        if self.shape not in {"arched", "high_arch", "low_arch", "angular", "straight", "ornate", "long", "short", "thick", "dense", "faded", "inward"}:
            raise ValueError("unknown eyebrow style")
