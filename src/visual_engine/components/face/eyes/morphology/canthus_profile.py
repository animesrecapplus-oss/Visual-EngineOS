from __future__ import annotations

"""Per-endpoint canthus tangent profiles.

V1.6 separates four geometric junctions that V1.5 treated as two coupled
upper/lower pairs.  The profile is deliberately renderer-neutral: it only
changes the local tangent used by the sampled lid and therefore the C1 bridge.

The values are authoring controls, not claims about anatomy or a universal
"anime" standard.  Reference calibration is intentionally a later step.
"""

from dataclasses import dataclass
import math


@dataclass(frozen=True, slots=True)
class CanthusEndpointTangentProfile:
    """Optional local tangent deformation for one lid/canthus junction.

    ``angle_deg`` rotates the existing local tangent in the eye's canonical
    frame. ``length_scale`` changes its magnitude. ``influence`` blends both
    changes with the V1.5-resolved tangent, making the default profile exactly
    backwards compatible.
    """

    angle_deg: float = 0.0
    length_scale: float = 1.0
    influence: float = 0.0

    def __post_init__(self) -> None:
        if not all(math.isfinite(v) for v in (self.angle_deg, self.length_scale, self.influence)):
            raise ValueError("canthus endpoint tangent profile must be finite")
        if not -45.0 <= self.angle_deg <= 45.0:
            raise ValueError("canthus endpoint tangent angle must be within [-45,45] degrees")
        if not 0.25 <= self.length_scale <= 2.0:
            raise ValueError("canthus endpoint tangent length_scale must be within [0.25,2]")
        if not 0.0 <= self.influence <= 1.0:
            raise ValueError("canthus endpoint tangent influence must be within [0,1]")

    @property
    def active(self) -> bool:
        """Whether this profile can change the V1.5 tangent."""
        return self.influence > 0.0 and (abs(self.angle_deg) > 0.0 or self.length_scale != 1.0)
