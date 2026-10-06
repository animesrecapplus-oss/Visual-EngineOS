from dataclasses import dataclass  # LASH-EFFECTS: immutable lash optical-effect specification.

from ..contracts.validation import _color, _finite  # LASH-CON: shared finite/color validation.

@dataclass(frozen=True, slots=True)  # LASH-CON-001: shadow specification is immutable.
class LashShadowSpec:  # CMP-EYE-LASHES: owns lash-cast shadow semantics.
    enabled: bool = True  # LASH-SHADOW: explicit effect enable state.
    color: str = "#000000"  # LASH-CON: shadow colour uses shared validation.
    opacity: float = 0.18  # LASH-CON: shadow opacity is bounded.
    density_response: float = 0.72  # LASH-CON: density response is non-negative.
    thickness_response: float = 0.58  # LASH-CON: thickness response is non-negative.
    length_response: float = 0.34  # LASH-CON: length response is non-negative.
    blur: float = 0.025  # LASH-CON: blur is non-negative.
    spread: float = 0.020  # LASH-CON: spread is non-negative.
    offset: float = 0.018  # LASH-CON: offset is non-negative.

    def __post_init__(self) -> None:  # LASH-CON: validate every shadow construction.
        vals = (self.opacity, self.density_response, self.thickness_response, self.length_response, self.blur, self.spread, self.offset)  # LASH-INV: collect all bounded values.
        if not _finite(vals) or any(v < 0 for v in vals):  # ADV-LASH-001: reject non-finite and negative state.
            raise ValueError("invalid lash shadow")  # ADV-LASH-001: fail explicitly on invalid state.
        if self.opacity > 1:  # LASH-INV: opacity cannot exceed one.
            raise ValueError("lash shadow opacity must be within [0,1]")  # LASH-INV: reject over-opacity.
        _color(self.color, "lash shadow color")  # LASH-CON: validate authored shadow colour.
