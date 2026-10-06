from __future__ import annotations

from dataclasses import dataclass
import math

from visual_engine.components.common.visual_contract import (
    LocalTransform,
    compose_matrices,
    identity_matrix,
    matrix_determinant,
    matrix_is_finite,
)
from visual_engine.runtime.geometry_contract_transform import Matrix3
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.scene.composition import Camera, Placement


@dataclass(frozen=True, slots=True)
class GeometryTransformResolution:
    """Immutable local/world/scene/camera transform result.

    The result owns transform-resolution values only; geometry-contract
    mutation remains in ``geometry_contract_transform``.
    """

    component_id: str
    local_to_world: Matrix3
    world_z: float
    world_to_camera: Matrix3
    local_to_camera: Matrix3
    camera_z: float
    scene_z: float

    def __post_init__(self) -> None:
        if not matrix_is_finite(self.local_to_world) or not matrix_is_finite(self.world_to_camera):
            raise ValueError("geometry transform matrices must be finite")
        if not matrix_is_finite(self.local_to_camera):
            raise ValueError("local_to_camera must be finite")
        for name, value in (("world_z", self.world_z), ("camera_z", self.camera_z), ("scene_z", self.scene_z)):
            if not math.isfinite(float(value)):
                raise ValueError(f"{name} must be finite")
        if abs(matrix_determinant(self.local_to_world)) <= 1e-15:
            raise ValueError("component local_to_world transform must be invertible")


def local_transform_matrix(transform: LocalTransform) -> Matrix3:
    """Convert one component-local transform to its affine matrix."""
    return transform.matrix()


def placement_matrix(placement: Placement) -> Matrix3:
    """Build the entity-to-scene affine transform."""
    angle = math.radians(placement.rotation)
    c, s = math.cos(angle), math.sin(angle)
    scale = float(placement.scale)
    return (
        (c * scale, -s * scale, float(placement.position.x)),
        (s * scale, c * scale, float(placement.position.y)),
        (0.0, 0.0, 1.0),
    )


def camera_matrix(camera: Camera) -> Matrix3:
    """Build the deterministic world/scene-to-camera affine transform."""
    angle = math.radians(-camera.rotation_deg)
    c, s = math.cos(angle), math.sin(angle)
    z = float(camera.zoom)
    return (
        (z * c, -z * s, z * (-camera.x * c + camera.y * s)),
        (z * s, z * c, z * (-camera.x * s - camera.y * c)),
        (0.0, 0.0, 1.0),
    )


def resolve_local_to_world(graph: RuntimeGraph, component_id: str) -> tuple[Matrix3, float]:
    """Compose root-to-target local transforms in deterministic parent order."""
    node = graph.get(component_id)
    chain = []
    current = node
    while True:
        chain.append(current.component)
        if current.parent_id is None:
            break
        current = graph.get(current.parent_id)
    chain.reverse()
    matrix = identity_matrix()
    world_z = 0.0
    for component in chain:
        matrix = compose_matrices(matrix, local_transform_matrix(component.transform))
        world_z += component.transform.z
    return matrix, world_z


def resolve_geometry_transform(
    graph: RuntimeGraph,
    component_id: str,
    *,
    placement: Placement | None = None,
    camera: Camera | None = None,
) -> GeometryTransformResolution:
    """Resolve local → world → scene → camera without mutating components."""
    local_to_world, world_z = resolve_local_to_world(graph, component_id)
    scene_matrix = placement_matrix(placement) if placement is not None else identity_matrix()
    world_to_camera = camera_matrix(camera or Camera())
    local_to_scene = compose_matrices(scene_matrix, local_to_world)
    local_to_camera = compose_matrices(world_to_camera, local_to_scene)
    scene_z = world_z + (placement.z if placement is not None else 0.0)
    camera_z = scene_z - (camera.z if camera is not None else 0.0)
    return GeometryTransformResolution(
        component_id, local_to_world, world_z, world_to_camera, local_to_camera, camera_z, scene_z
    )
