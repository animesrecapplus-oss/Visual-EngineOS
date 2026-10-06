from dataclasses import dataclass  # PUPIL-EFFECTS: immutable optical-effect specifications.

from ..contracts.validation import _color, _finite  # PUPIL-EFFECTS: shared finite/color validation.

@dataclass(frozen=True, slots=True)  # PUPIL-CON-005: glow is an immutable value specification.
class PupilGlowSpec:  # CMP-EYE-PUPIL: owns pupil-specific glow parameters.
    enabled: bool = False  # PUPIL-GLOW: explicit enable state.
    color: str = "#ffffff"  # INV-PUPIL-004: glow colour uses shared validation.
    intensity: float = 0.0  # INV-PUPIL-003: glow intensity is bounded.
    radius: float = 1.8  # INV-PUPIL: non-negative optical footprint radius.
    blur: float = 0.12  # INV-PUPIL: non-negative optical blur.
    core_intensity: float = 0.0  # INV-PUPIL-003: core intensity is bounded.
    core_radius: float = 0.55  # INV-PUPIL: non-negative core footprint radius.

    def __post_init__(self) -> None:  # PUPIL-CON: validate every glow construction.
        vals = (self.intensity, self.radius, self.blur, self.core_intensity, self.core_radius)  # INV-PUPIL: collect every numeric glow value.
        if not _finite(vals) or any(v < 0 for v in vals):  # ADV-PUPIL-001/005: reject non-finite and negative values.
            raise ValueError("invalid pupil glow")  # ADV-PUPIL-001/005: fail explicitly on invalid glow state.
        if self.intensity > 1 or self.core_intensity > 1:  # INV-PUPIL-003: enforce unit upper bounds.
            raise ValueError("pupil glow intensity must be within [0,1]")  # INV-PUPIL-003: reject over-intensity.
        _color(self.color, "pupil glow color")  # INV-PUPIL-004: validate authored glow colour.

@dataclass(frozen=True, slots=True)  # PUPIL-CON-005: smoke is an immutable value specification.
class PupilSmokeSpec:  # CMP-EYE-PUPIL: owns pupil-specific smoke parameters.
    enabled: bool = False  # PUPIL-SMOKE: explicit enable state.
    color: str = "#ffffff"  # INV-PUPIL-004: smoke colour uses shared validation.
    opacity: float = 0.0  # INV-PUPIL-003: smoke opacity is bounded.
    length: float = 0.45  # INV-PUPIL: non-negative smoke length.
    width: float = 0.08  # INV-PUPIL: non-negative smoke width.
    curl: float = 0.18  # INV-PUPIL: non-negative smoke curl.
    direction_deg: float = -90.0  # PUPIL-SMOKE: direction is finite but may be negative.
    wisps: int = 3  # INV-PUPIL-007: at least one wisp is required.

    def __post_init__(self) -> None:  # PUPIL-CON: validate every smoke construction.
        vals = (self.opacity, self.length, self.width, self.curl, self.direction_deg)  # INV-PUPIL: collect every numeric smoke value.
        if not _finite(vals) or any(v < 0 for v in (self.opacity, self.length, self.width, self.curl)):  # ADV-PUPIL-001/005: reject non-finite and negative state.
            raise ValueError("invalid pupil smoke")  # ADV-PUPIL-001/005: fail explicitly on invalid smoke state.
        if self.opacity > 1 or self.wisps < 1:  # INV-PUPIL-003/007: enforce opacity and count bounds.
            raise ValueError("invalid pupil smoke bounds")  # INV-PUPIL-003/007: reject impossible smoke state.
        _color(self.color, "pupil smoke color")  # INV-PUPIL-004: validate authored smoke colour.
