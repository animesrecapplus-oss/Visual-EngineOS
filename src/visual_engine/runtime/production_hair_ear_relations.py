from __future__ import annotations

"""Production orchestration for the certified Hair -> Ear relations.

The leaf pair resolver remains the semantic owner of one relation. This module
only owns the existing two-Ear production orchestration and preserves its order.
"""

from collections.abc import Callable, Mapping

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.meta import Component
from visual_engine.components.common.visual_contract import ResolvedVisualContract
from visual_engine.runtime.production_hair_ear_occlusion import (
    ProductionHairEarOcclusion,
    resolve_hair_ear_occlusion,
)
from visual_engine.runtime.production_owner_geometry import extract_production_owner_geometry

OwnerGeometryResolver = Callable[[GeometryContract, str], tuple[GeometryContract, float]]


def resolve_production_hair_ear_relations(
    root: Component,
    camera_geometry: GeometryContract,
    styles: Mapping[str, ResolvedVisualContract],
    *,
    owner_geometry: OwnerGeometryResolver = extract_production_owner_geometry,
) -> tuple[ProductionHairEarOcclusion, ...]:
    """Resolve the real Hair -> left/right Ear relations in stable order."""
    if not isinstance(root, Component):
        raise TypeError("Hair/Ear production relations require a Component root")
    if not isinstance(camera_geometry, GeometryContract):
        raise TypeError("Hair/Ear production relations require GeometryContract camera geometry")
    if not isinstance(styles, Mapping):
        raise TypeError("Hair/Ear production relations require a style mapping")
    if not callable(owner_geometry):
        raise TypeError("owner_geometry must be callable")

    hair = root.find("hair")
    if hair is None:
        raise ValueError("Hair/Ear production occlusion requires the real Hair child")
    hair_style = styles.get(hair.id)
    if not isinstance(hair_style, ResolvedVisualContract):
        raise ValueError(f"Hair/Ear production occlusion requires resolved style for {hair.id!r}")
    hair_geometry, hair_depth = owner_geometry(camera_geometry, hair.id)

    results: list[ProductionHairEarOcclusion] = []
    for ear_id in ("left_ear", "right_ear"):
        ear = root.find(ear_id)
        if ear is None:
            raise ValueError(f"Ear production occlusion requires component {ear_id!r}")
        ear_geometry, ear_depth = owner_geometry(camera_geometry, ear.id)
        results.append(resolve_hair_ear_occlusion(
            ear, ear_geometry, ear_depth, hair, hair_geometry, hair_depth,
            hair_opacity=hair_style.effective_visibility,
            hair_transmission=hair_style.material.transmission,
        ))
    return tuple(results)
