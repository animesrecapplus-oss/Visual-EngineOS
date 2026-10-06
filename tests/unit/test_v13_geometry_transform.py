from math import isclose

import pytest

from visual_engine.components.common.geometry_contract import GeometryBounds, GeometryContract, GeometryPath, GeometryPrimitive
from visual_engine.model import Component, LocalTransform
from visual_engine.runtime import (
    RuntimeGraph, resolve_geometry_contract, resolve_geometry_transform, transform_geometry_contract,
)
from visual_engine.scene import Camera, Placement
from visual_engine.math import Vec2


def _unit_geometry():
    return GeometryContract(
        coordinate_frame="component",
        bounds=GeometryBounds(-1, -2, 1, 2),
        paths=(GeometryPath((("M", (-1, 0)), ("C", (-1, 1, 0, 2, 1, 2)), ("Z", ()))),),
        primitives=(GeometryPrimitive("ellipse", {"cx": 0, "cy": 0, "rx": 1, "ry": 0.5}),),
        anchors={"center": (0, 0, 0), "top": (0, -2, 0)},
    )


def test_hierarchy_local_to_world_composes_transforms_in_order():
    root = Component("root", "face", transform=LocalTransform(x=10, y=20, rotation_deg=90))
    child = Component("child", "eye", transform=LocalTransform(x=5, y=0, rotation_deg=30, scale_x=2, scale_y=3, z=4))
    root.add_child(child)
    resolution = resolve_geometry_transform(RuntimeGraph.from_component(root), "child")
    x, y = resolution.local_to_world[0][2], resolution.local_to_world[1][2]
    assert isclose(x, 10, abs_tol=1e-12)
    assert isclose(y, 25, abs_tol=1e-12)
    assert isclose(resolution.world_z, 4)


def test_transform_contract_moves_paths_anchors_and_bounds():
    geometry = _unit_geometry()
    root = Component("root", "face", transform=LocalTransform(x=10, y=20, rotation_deg=90, scale_x=2, scale_y=2))
    graph = RuntimeGraph.from_component(root)
    world = resolve_geometry_contract(graph, "root", geometry)
    assert world.coordinate_frame == "world"
    assert world.anchors["center"] == (10.0, 20.0, 0.0)
    assert world.anchors["top"] == (14.0, 20.0, 0.0)
    assert world.bounds.min_x == 6.0
    assert world.bounds.max_x == 14.0


def test_placement_and_camera_are_separate_from_component_transform():
    root = Component("root", "face", transform=LocalTransform(x=2, y=3))
    graph = RuntimeGraph.from_component(root)
    placement = Placement("entity", Vec2(100, 50), scale=2, rotation=90, z=7)
    camera = Camera(x=100, y=50, zoom=2, rotation_deg=0, z=3)
    resolution = resolve_geometry_transform(graph, "root", placement=placement, camera=camera)
    # Component origin -> scene (100+2*2, 50+3*2) -> camera centered at 100/50.
    x, y = resolution.local_to_camera[0][2], resolution.local_to_camera[1][2]
    assert isclose(x, -12.0, abs_tol=1e-12)
    assert isclose(y, 8.0, abs_tol=1e-12)
    assert isclose(resolution.scene_z, 7)
    assert isclose(resolution.camera_z, 4)


def test_camera_rotation_is_applied_in_opposite_direction():
    root = Component("root", "face")
    graph = RuntimeGraph.from_component(root)
    camera = Camera(rotation_deg=90)
    resolution = resolve_geometry_transform(graph, "root", camera=camera)
    x, y = resolution.local_to_camera[0][0], resolution.local_to_camera[1][0]
    assert isclose(x, 0, abs_tol=1e-12)
    assert isclose(y, -1, abs_tol=1e-12)


def test_non_uniform_scale_turns_circle_into_ellipse_without_losing_center():
    geometry = GeometryContract(primitives=(GeometryPrimitive("ellipse", {"cx": 1, "cy": 2, "rx": 2, "ry": 2, "shape": "circle"}),))
    matrix = ((2.0, 0.0, 0.0), (0.0, 3.0, 0.0), (0.0, 0.0, 1.0))
    transformed = transform_geometry_contract(geometry, matrix)
    primitive = transformed.primitives[0]
    assert isclose(primitive.data["cx"], 2)
    assert isclose(primitive.data["cy"], 6)
    assert isclose(primitive.data["rx"], 6)
    assert isclose(primitive.data["ry"], 4)
    assert primitive.data["shape"] == "ellipse"


def test_rotation_preserves_curve_command_arity():
    geometry = GeometryContract(paths=(GeometryPath((("C", (0, 0, 1, 0, 1, 1)),)),))
    matrix = ((0.0, -1.0, 0.0), (1.0, 0.0, 0.0), (0.0, 0.0, 1.0))
    transformed = transform_geometry_contract(geometry, matrix)
    assert transformed.paths[0].commands[0][1] == (0.0, 0.0, 0.0, 1.0, -1.0, 1.0)


def test_unknown_geometric_primitive_fails_closed():
    geometry = GeometryContract(primitives=(GeometryPrimitive("mystery_shape", {"x": 1}),))
    with pytest.raises(ValueError, match="unsupported transformable"):
        transform_geometry_contract(geometry, ((1,0,0),(0,1,0),(0,0,1)))
