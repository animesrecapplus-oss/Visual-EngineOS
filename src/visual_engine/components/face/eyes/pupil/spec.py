import math  # PUPIL-CON: finite validation without coercive conversion.
from dataclasses import dataclass, field  # PUPIL-SPEC: immutable specification primitives.
from numbers import Real  # PUPIL-CON: accept numeric values without coercing strings/bools.

from ..contracts.types import PupilShape  # PUPIL-CON: canonical pupil shape type.
from ..contracts.validation import _color  # PUPIL-CON: shared colour validation remains canonical.
from .effects import PupilGlowSpec, PupilSmokeSpec  # PUPIL-REL: pupil optical effects are child specifications.

@dataclass(frozen=True, slots=True)  # PUPIL-CON-005: specifications are immutable value objects.
class PupilSpec:  # CMP-EYE-PUPIL: owns validated local pupil parameters.
    x: float = 0.0  # PUPIL-CON: local horizontal offset.
    y: float = 0.0  # PUPIL-CON: local vertical offset.
    scale: float = 1.0  # INV-PUPIL-002: global pupil scale must stay positive.
    scale_x: float = 1.0  # INV-PUPIL-002: horizontal scale must stay positive.
    scale_y: float = 1.0  # INV-PUPIL-002: vertical scale must stay positive.
    rotation_deg: float = 0.0  # PUPIL-CON: local screen-space orientation value.
    shape: PupilShape = "ellipse"  # PUPIL-CON: shape vocabulary comes from the shared type.
    color: str = "#000000"  # INV-PUPIL-004: pupil colour uses shared validation.
    outline_color: str = "#000000"  # INV-PUPIL-004: outline colour uses shared validation.
    outline_width: float = 0.008  # INV-PUPIL-002: outline width may be zero but not negative.
    opacity: float = 1.0  # INV-PUPIL-003: opacity is bounded to the unit interval.
    glow: PupilGlowSpec = field(default_factory=PupilGlowSpec)  # PUPIL-REL: optional glow child value.
    smoke: PupilSmokeSpec = field(default_factory=PupilSmokeSpec)  # PUPIL-REL: optional smoke child value.

    def __post_init__(self) -> None:  # PUPIL-CON: validate every local construction.
        numeric = (self.x, self.y, self.scale, self.scale_x, self.scale_y, self.rotation_deg, self.outline_width, self.opacity)
        if any(isinstance(value, bool) or not isinstance(value, Real) or not math.isfinite(value) for value in numeric):  # INV-PUPIL-001: strict one-pass numeric/finite validation avoids coercive strings.
            raise ValueError("Pupil values must be finite numeric values")  # ADV-PUPIL-001: fail explicitly instead of propagating invalid state.
        if self.scale <= 0 or self.scale_x <= 0 or self.scale_y <= 0 or self.outline_width < 0 or not 0 <= self.opacity <= 1:  # INV-PUPIL-002/003: enforce scale, outline and opacity bounds.
            raise ValueError("invalid pupil")  # INV-PUPIL-002/003: reject impossible local state.
        _color(self.color, "pupil color")  # INV-PUPIL-004: validate authored pupil colour.
        _color(self.outline_color, "pupil outline color")  # INV-PUPIL-004: validate authored outline colour.
