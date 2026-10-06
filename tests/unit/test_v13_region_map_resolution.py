from __future__ import annotations

from visual_engine.components.common.geometry_contract import GeometryBounds, GeometryContract, GeometryPrimitive
from visual_engine.components.common.meta import Component
from visual_engine.math import Vec2
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.region_maps import SemanticRegionProviderRegistry, generic_region_provider, resolve_region_map
from visual_engine.scene.composition import Camera, Placement


def _graph() -> RuntimeGraph:
    root = Component("root", "Root")
    child = Component("target", "Thing")
    child.geometry = GeometryContract(
        coordinate_frame="component", bounds=GeometryBounds(0, 0, 10, 10),
        primitives=(GeometryPrimitive("polygon", {"semantic_region": "surface", "points": ((0,0),(10,0),(10,10),(0,10))}),),
    )
    root.add_child(child)
    return RuntimeGraph.from_component(root)


def _registry() -> SemanticRegionProviderRegistry:
    registry = SemanticRegionProviderRegistry()
    registry.register(generic_region_provider(kinds=("Thing",)))
    return registry


def test_region_map_is_local_and_renderer_independent():
    graph = _graph()
    result = resolve_region_map(graph, "target", graph.get("target").component.geometry, _registry(), target="local")
    region = result.region_map.regions[0]
    assert result.coordinate_frame == "local"
    assert region.name == "surface"
    assert region.geometry.coordinate_frame == "component"
    assert region.geometry.primitives[0].data["points"][0] == (0, 0)


def test_region_map_follows_hierarchy_and_scene_placement():
    graph = _graph()
    placement = Placement("entity", Vec2(100, 50), scale=2, rotation=90, z=7)
    result = resolve_region_map(graph, "target", graph.get("target").component.geometry, _registry(), placement=placement, target="scene")
    points = result.region_map.regions[0].geometry.primitives[0].data["points"]
    assert points[0] == (100.0, 50.0)
    assert points[1] == (100.0, 70.0)
    assert points[2] == (80.0, 70.0)
    assert result.region_map.regions[0].geometry.coordinate_frame == "scene"


def test_region_map_resolves_directly_to_camera_frame():
    graph = _graph()
    placement = Placement("entity", Vec2(100, 50), scale=2)
    camera = Camera(x=100, y=50, zoom=2)
    result = resolve_region_map(graph, "target", graph.get("target").component.geometry, _registry(), placement=placement, camera=camera, target="camera")
    points = result.region_map.regions[0].geometry.primitives[0].data["points"]
    assert points[0] == (0.0, 0.0)
    assert points[1] == (40.0, 0.0)


def test_unknown_component_kind_has_no_implicit_region_provider():
    graph = _graph()
    root_geometry = graph.get("root").component.geometry
    try:
        resolve_region_map(graph, "root", root_geometry, _registry())
    except KeyError as exc:
        assert "Root" in str(exc)
    else:
        raise AssertionError("expected no provider for Root")
