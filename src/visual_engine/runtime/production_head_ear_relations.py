from __future__ import annotations

"""Production orchestration for the existing two-Ear Head/Ear relation."""

from collections.abc import Callable

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.meta import Component
from visual_engine.components.common.visual_contract import ResolvedVisualContract
from visual_engine.runtime.production_head_ear_occlusion import (
    ProductionHeadEarOcclusion,
    resolve_head_ear_occlusion,
)

OwnerGeometryResolver = Callable[[GeometryContract, str], tuple[GeometryContract, float]]


def resolve_production_head_ear_relations(
    root: Component,
    camera_geometry: GeometryContract,
    head_style: ResolvedVisualContract,
    *,
    owner_geometry: OwnerGeometryResolver,
) -> tuple[ProductionHeadEarOcclusion, ...]:
    """Orchestrate the two real Head/Ear leaf relations in stable order.

    Geometry, appearance and visibility semantics remain owned by their existing
    canonical components; this adapter only preserves the production relation order.
    """
    if not isinstance(root, Component):
        raise TypeError("Head/Ear relations require a Component root")
    if not isinstance(camera_geometry, GeometryContract):
        raise TypeError("camera_geometry must be a GeometryContract")
    if not isinstance(head_style, ResolvedVisualContract):
        raise TypeError("head_style must be a ResolvedVisualContract")
    if not callable(owner_geometry):
        raise TypeError("owner_geometry must be callable")

    head_geometry, head_depth = owner_geometry(camera_geometry, root.id)
    if not isinstance(head_geometry, GeometryContract):
        raise TypeError("owner_geometry must return GeometryContract, depth")
    if not isinstance(head_depth, (int, float)) or isinstance(head_depth, bool):
        raise TypeError("owner_geometry depth must be numeric")

    relations: list[ProductionHeadEarOcclusion] = []
    for ear_id in ("left_ear", "right_ear"):
        ear = root.find(ear_id)
        if ear is None:
            raise ValueError(f"Ear production occlusion requires component {ear_id!r}")
        ear_geometry, ear_depth = owner_geometry(camera_geometry, ear.id)
        if not isinstance(ear_geometry, GeometryContract):
            raise TypeError("owner_geometry must return GeometryContract, depth")
        if not isinstance(ear_depth, (int, float)) or isinstance(ear_depth, bool):
            raise TypeError("owner_geometry depth must be numeric")
        relations.append(resolve_head_ear_occlusion(
            ear,
            ear_geometry,
            ear_depth,
            root,
            head_geometry,
            head_depth,
            head_opacity=head_style.effective_visibility,
            head_transmission=head_style.material.transmission,
        ))
    return tuple(relations)
