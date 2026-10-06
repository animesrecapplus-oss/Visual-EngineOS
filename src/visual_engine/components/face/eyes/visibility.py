from __future__ import annotations

"""Hierarchical visibility intent for every named ocular granularity.

A false parent disables its entire descendant subtree. Sibling features are
unaffected, so ``pupils=false`` does not disable highlights, lashes or brows.
Visibility is presentation intent, not geometry identity; toggling it must not
force a geometry-cache rebuild.
"""

from dataclasses import dataclass, field
from typing import Mapping

PARENT: Mapping[str, str | None] = {
    "eye": None, "sclera": "eye", "contour": "eye",
    "upper_lid": "contour", "lower_lid": "contour",
    "canthi": "contour", "inner_canthus": "canthi", "outer_canthus": "canthi",
    "epicanthic_fold": "canthi",
    "medial_caruncle": "inner_canthus",
    "eyelid": "eye", "upper_crease": "eyelid", "lower_crease": "eyelid",
    "iris": "eye", "limbal_ring": "iris", "crypts": "iris", "fibres": "iris",
    "radial_structure": "iris", "pigmentation": "iris", "rings": "iris", "microstructure": "iris",
    "pupil": "eye", "pupil_glow": "pupil", "pupil_smoke": "pupil",
    "highlight": "eye", "reflection": "highlight", "reflection_marks": "highlight",
    "lashes": "eye", "lower_lashes": "eye", "eyebrow": "eye",
    "sclera_spots": "sclera", "under_eye_marks": "eye",
}

@dataclass(frozen=True, slots=True)
class EyeVisibilitySpec:
    """Sparse explicit overrides; unspecified nodes default to visible."""
    overrides: Mapping[str, bool] = field(default_factory=dict)

    def __post_init__(self) -> None:
        values = dict(self.overrides)
        unknown = sorted(set(values) - set(PARENT))
        if unknown:
            raise ValueError(f"unknown eye visibility nodes: {unknown}")
        if any(not isinstance(v, bool) for v in values.values()):
            raise TypeError("eye visibility values must be bool")
        object.__setattr__(self, "overrides", values)

    def is_visible(self, node: str) -> bool:
        if node not in PARENT:
            raise ValueError(f"unknown eye visibility node: {node}")
        current: str | None = node
        while current is not None:
            value = self.overrides.get(current)
            if value is False:
                return False
            current = PARENT[current]
        return True

    def resolved(self) -> Mapping[str, bool]:
        return {node: self.is_visible(node) for node in PARENT}
