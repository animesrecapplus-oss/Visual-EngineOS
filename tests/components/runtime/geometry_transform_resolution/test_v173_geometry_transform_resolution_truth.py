from __future__ import annotations

import math

import pytest

from visual_engine.entities import build_human_face
from visual_engine.runtime import (
    GeometryTransformResolution,
    RuntimeGraph,
    camera_matrix,
    local_transform_matrix,
    placement_matrix,
    resolve_geometry_transform,
    resolve_local_to_world,
)
from visual_engine.runtime.geometry_transform_resolution import GeometryTransformResolution as Canonical
from visual_engine.scene.composition import Camera, Placement
from visual_engine.math import Vec2


def test_canonical_owner_and_public_identity() -> None:
    assert GeometryTransformResolution is Canonical
    assert resolve_geometry_transform.__module__.endswith("geometry_transform_resolution")


def test_resolution_is_frozen_and_finite() -> None:
    graph = RuntimeGraph.from_component(build_human_face("face-01"))
    result = resolve_geometry_transform(graph, "face-01")
    assert isinstance(result, GeometryTransformResolution)
    assert all(math.isfinite(v) for v in (result.world_z, result.scene_z, result.camera_z))
    with pytest.raises((AttributeError, TypeError)):
        result.world_z = 4.0


def test_parent_chain_and_public_matrix_helpers_remain_consistent() -> None:
    graph = RuntimeGraph.from_component(build_human_face("face-01"))
    matrix, world_z = resolve_local_to_world(graph, "face-01")
    result = resolve_geometry_transform(graph, "face-01")
    assert matrix == result.local_to_world
    assert world_z == result.world_z
    assert len(local_transform_matrix(graph.get("face-01").component.transform)) == 3
    assert len(placement_matrix(Placement("face-01", Vec2(0.0, 0.0)))) == 3
    assert len(camera_matrix(Camera())) == 3


def test_non_finite_component_depth_is_rejected() -> None:
    graph = RuntimeGraph.from_component(build_human_face("face-01"))
    with pytest.raises(ValueError):
        GeometryTransformResolution("face-01", ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)), math.nan, ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)), ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)), 0.0, 0.0)
