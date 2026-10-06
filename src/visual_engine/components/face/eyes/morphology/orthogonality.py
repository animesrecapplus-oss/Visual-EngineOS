from __future__ import annotations

"""Executable MOR parameter-orthogonality contract.

Orthogonality means declared causal scope, not pixel similarity. A morphology
parameter is allowed to change only semantic geometry projections named by its
contract. Endpoint and bridge effects are separated because a lid curve may need
to alter a bridge tangent while leaving the anatomical corner location unchanged.
"""

from dataclasses import dataclass
from typing import Callable, Mapping

from ..geometry.types import EyeGeometry
from .spec import EyeParameters

Channel = str
Parameter = str
MORPH_CHANNELS: tuple[Channel, ...] = (
    "upper_margin", "lower_margin", "inner_canthus_endpoint", "outer_canthus_endpoint",
    "inner_canthus_bridge", "outer_canthus_bridge", "upper_crease", "lower_crease",
    "iris", "pupil", "epicanthic_fold", "medial_caruncle",
)

ALLOWED_CHANNELS: Mapping[Parameter, frozenset[Channel]] = {
    "width": frozenset(MORPH_CHANNELS),
    "height": frozenset(MORPH_CHANNELS),
    "opening": frozenset(MORPH_CHANNELS),
    "upper_curve": frozenset({"upper_margin", "upper_crease", "inner_canthus_bridge", "outer_canthus_bridge"}),
    "lower_curve": frozenset({"lower_margin", "lower_crease", "inner_canthus_bridge", "outer_canthus_bridge"}),
    "asymmetry": frozenset({"upper_margin", "lower_margin", "upper_crease", "lower_crease", "inner_canthus_bridge", "outer_canthus_bridge"}),
    "rotation_deg": frozenset(MORPH_CHANNELS),
    "contour_irregularity": frozenset({"upper_margin", "lower_margin", "upper_crease", "lower_crease", "inner_canthus_bridge", "outer_canthus_bridge"}),
    "contour_wave_amplitude": frozenset({"upper_margin", "lower_margin", "upper_crease", "lower_crease", "inner_canthus_bridge", "outer_canthus_bridge"}),
    "contour_wave_frequency": frozenset({"upper_margin", "lower_margin", "upper_crease", "lower_crease", "inner_canthus_bridge", "outer_canthus_bridge"}),
    "canthus_inner_roundness": frozenset({"upper_margin", "lower_margin", "inner_canthus_endpoint", "inner_canthus_bridge", "epicanthic_fold", "medial_caruncle"}),
    "canthus_outer_roundness": frozenset({"upper_margin", "lower_margin", "outer_canthus_endpoint", "outer_canthus_bridge"}),
    "epicanthic_fold": frozenset({"epicanthic_fold"}),
}

@dataclass(frozen=True, slots=True)
class OrthogonalityReport:
    parameter: str
    changed_channels: tuple[Channel, ...]
    contaminated_channels: tuple[Channel, ...]
    @property
    def valid(self) -> bool:
        return not self.contaminated_channels


def _projection(g: EyeGeometry) -> dict[Channel, object]:
    return {
        "upper_margin": g.upper_lid_points, "lower_margin": g.lower_lid_points,
        "inner_canthus_endpoint": g.inner_canthus, "outer_canthus_endpoint": g.outer_canthus,
        "inner_canthus_bridge": g.inner_canthus_bridge, "outer_canthus_bridge": g.outer_canthus_bridge,
        "upper_crease": g.upper_crease_points, "lower_crease": g.lower_crease_points,
        "iris": (g.iris_center, g.iris_rx, g.iris_ry),
        "pupil": (g.pupil_centers, g.pupil_radii),
        "epicanthic_fold": g.epicanthic_fold_points,
        "medial_caruncle": g.medial_caruncle_points,
    }

def assess_parameter_orthogonality(parameter: str, base: EyeParameters, changed: EyeParameters, build: Callable[[EyeParameters], EyeGeometry]) -> OrthogonalityReport:
    """Compare semantic projections and reject undeclared causal coupling."""
    allowed = ALLOWED_CHANNELS.get(parameter)
    if allowed is None:
        raise ValueError(f"no orthogonality contract for morphology parameter: {parameter}")
    before, after = _projection(build(base)), _projection(build(changed))
    changed_channels = tuple(c for c in MORPH_CHANNELS if before[c] != after[c])
    contaminated = tuple(c for c in changed_channels if c not in allowed)
    return OrthogonalityReport(parameter, changed_channels, contaminated)
