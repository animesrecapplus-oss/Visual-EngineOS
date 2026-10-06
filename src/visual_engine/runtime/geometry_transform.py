from __future__ import annotations

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.visual_contract import compose_matrices, identity_matrix
from visual_engine.runtime.geometry_contract_transform import Matrix3, transform_geometry_contract
from visual_engine.runtime.geometry_transform_resolution import (
    GeometryTransformResolution, camera_matrix, local_transform_matrix, placement_matrix,
    resolve_geometry_transform, resolve_local_to_world,
)
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.scene.composition import Camera, Placement

# Compatibility facade: transform resolution has one owner; this module owns only
# placement of an already generated GeometryContract into the requested frame.

def resolve_geometry_contract(
    graph: RuntimeGraph,
    component_id: str,
    geometry: GeometryContract,
    *,
    placement: Placement | None = None,
    camera: Camera | None = None,
    target: str = "world",
) -> GeometryContract:
    """Place component-local geometry into world, scene or camera coordinates."""
    resolution = resolve_geometry_transform(graph, component_id, placement=placement, camera=camera)
    if target == "world":
        matrix = resolution.local_to_world
        z = resolution.world_z
        frame = "world"
    elif target == "scene":
        placement_matrix_value = placement_matrix(placement) if placement is not None else identity_matrix()
        matrix = compose_matrices(placement_matrix_value, resolution.local_to_world)
        z = resolution.scene_z
        frame = "scene"
    elif target == "camera":
        matrix = resolution.local_to_camera
        z = resolution.camera_z
        frame = "camera"
    else:
        raise ValueError("target must be world, scene or camera")
    return transform_geometry_contract(geometry, matrix, z_offset=z, coordinate_frame=frame)

__all__ = [
    "GeometryTransformResolution", "Matrix3", "camera_matrix", "local_transform_matrix",
    "placement_matrix", "resolve_geometry_contract", "resolve_geometry_transform",
    "resolve_local_to_world",
]
