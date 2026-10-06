from __future__ import annotations

from dataclasses import dataclass

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.runtime.geometry_transform import GeometryTransformResolution, resolve_geometry_transform, resolve_geometry_contract
from visual_engine.components.face.eyes.geometry.runtime_transform import resolve_alignment_axis_rotation, resolve_ocular_basis
from visual_engine.runtime.graph import RuntimeGraph


@dataclass(frozen=True, slots=True)
class OcularTransformResolution:
    """Eye-specific façade over the runtime's authoritative world transform.

    The eye domain does not reimplement parent composition. It consumes the same
    root→target matrix as every other component, so a face rotation/scale/translation
    cannot silently diverge between brow, lid and generic geometry paths.
    """

    component_id: str
    runtime: GeometryTransformResolution
    ocular_basis: object
    alignment_axis_rotation_deg: float

    @property
    def local_to_world(self):
        return self.runtime.local_to_world

    @property
    def world_z(self) -> float:
        return self.runtime.world_z


def resolve_ocular_transform(graph: RuntimeGraph, component_id: str) -> OcularTransformResolution:
    runtime = resolve_geometry_transform(graph, component_id)
    return OcularTransformResolution(
        component_id,
        runtime,
        resolve_ocular_basis(graph, component_id),
        resolve_alignment_axis_rotation(graph, component_id),
    )


def resolve_ocular_geometry(
    graph: RuntimeGraph,
    component_id: str,
    geometry: GeometryContract,
    *,
    target: str = "world",
) -> GeometryContract:
    """Resolve an eye's renderer-neutral geometry through the existing scene graph."""
    return resolve_geometry_contract(graph, component_id, geometry, target=target)
