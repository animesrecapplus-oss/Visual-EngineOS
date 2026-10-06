from __future__ import annotations

"""Production orchestration for the existing Head→child overlap relation."""

from collections.abc import Callable
import math

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.meta import Component
from visual_engine.runtime.production_face_overlap_visibility import (
    ProductionVisibilityResolution,
    resolve_face_overlap_visibility,
)

OwnerGeometryResolver = Callable[[GeometryContract, str], tuple[GeometryContract, float]]

# These are the generator variants already proven to consume the production
# Head→child overlap result. Unknown generators must not silently acquire proof.
_FACE_OVERLAP_OCCLUDERS: dict[str, tuple[str, ...]] = {
    "face.human_with_eyes_nose": ("nose",),
    "face.human_with_eyes_nose_mouth": ("nose", "mouth"),
    "face.human_with_eyes_nose_mouth_ears": ("nose", "mouth"),
    "face.human_with_eyes_nose_mouth_ears_hair": ("nose", "mouth"),
}


def resolve_production_face_overlap_relations(
    root: Component,
    camera_geometry: GeometryContract,
    generator: str,
    *,
    owner_geometry: OwnerGeometryResolver,
) -> ProductionVisibilityResolution | None:
    """Orchestrate the existing production Head→child overlap variants.

    The adapter only selects the already-proven child set for a generator and
    delegates the actual visibility/attribution contract to its canonical owner.
    """
    if not isinstance(root, Component):
        raise TypeError("face overlap relations require a Component root")
    if not isinstance(camera_geometry, GeometryContract):
        raise TypeError("face overlap relations require a GeometryContract")
    if not isinstance(generator, str) or not generator:
        raise TypeError("face overlap relations generator must be a non-empty string")
    if not callable(owner_geometry):
        raise TypeError("face overlap relations owner_geometry must be callable")
    occluders = _FACE_OVERLAP_OCCLUDERS.get(generator)
    if occluders is None:
        return None

    def checked_owner_geometry(geometry: GeometryContract, owner_id: str) -> tuple[GeometryContract, float]:
        resolved_geometry, depth = owner_geometry(geometry, owner_id)
        if not isinstance(resolved_geometry, GeometryContract):
            raise TypeError("owner_geometry must return GeometryContract, depth")
        if isinstance(depth, bool) or not isinstance(depth, (int, float)) or not math.isfinite(depth):
            raise ValueError("owner_geometry depth must be finite numeric")
        return resolved_geometry, float(depth)

    return resolve_face_overlap_visibility(
        root, camera_geometry, occluders, owner_geometry=checked_owner_geometry
    )
