import pytest

from visual_engine.components.face.generators import (
    EYE_PAIR_GEOMETRY_GENERATOR,
    FACE_GEOMETRY_GENERATOR,
    FACE_WITH_EYES_GEOMETRY_GENERATOR,
    FaceWithEyesGeometryInputs,
    default_face_geometry_registry,
)
from visual_engine.entities import build_human_face
from visual_engine.model import Component, GeometryContract, Parameter
from visual_engine.runtime import CachedGeometryGenerator, GeometryCache, GeometryGeneratorRegistry, RegisteredGeometryGenerator, RuntimeGraph


def _face_graph():
    return RuntimeGraph.from_component(build_human_face("face-01"))


def test_explicit_generator_alternatives_do_not_replace_default():
    registry = default_face_geometry_registry()
    assert registry.defaults()["HumanFace"] == FACE_GEOMETRY_GENERATOR
    assert registry.defaults()["eye"] == "face.eye"
    assert registry.defaults()["Eye"] == "face.eye"
    assert registry.get(EYE_PAIR_GEOMETRY_GENERATOR).name == EYE_PAIR_GEOMETRY_GENERATOR
    assert registry.get(FACE_WITH_EYES_GEOMETRY_GENERATOR).name == FACE_WITH_EYES_GEOMETRY_GENERATOR


def test_face_default_generator_produces_head_geometry():
    graph = _face_graph()
    service = CachedGeometryGenerator(default_face_geometry_registry(), GeometryCache(max_entries=16))
    result = service.generate(graph, "face-01")
    assert isinstance(result.geometry, GeometryContract)
    assert result.geometry.paths
    assert result.geometry.surfaces[0].name == "head"
    assert result.cache_hit is False


def test_eye_pair_generator_recursively_generates_both_eye_children():
    graph = _face_graph()
    service = CachedGeometryGenerator(default_face_geometry_registry(), GeometryCache(max_entries=32))
    result = service.generate(graph, "face-01", generator=EYE_PAIR_GEOMETRY_GENERATOR)
    assert result.cache_hit is False
    assert {p.data["component_id"] for p in result.geometry.primitives} >= {"left_eye", "right_eye"}
    assert {s.data["component_id"] for s in result.geometry.surfaces} >= {"left_eye", "right_eye"}
    second = service.generate(graph, "face-01", generator=EYE_PAIR_GEOMETRY_GENERATOR)
    assert second.cache_hit is True
    assert second.geometry is result.geometry
    assert service.cache.stats().builds == 3  # two eyes + pair


def test_eye_pair_cache_invalidates_when_one_eye_geometry_changes():
    face = build_human_face("face-01")
    graph = RuntimeGraph.from_component(face)
    service = CachedGeometryGenerator(default_face_geometry_registry(), GeometryCache(max_entries=32))
    first = service.generate(graph, "face-01", generator=EYE_PAIR_GEOMETRY_GENERATOR)
    graph.get("left_eye").component.parameters["width"] = Parameter("width", 0.90, 0.05, 1.0)
    second = service.generate(graph, "face-01", generator=EYE_PAIR_GEOMETRY_GENERATOR)
    assert second.cache_hit is False
    assert second.key != first.key
    assert service.cache.stats().builds == 5


def test_eye_pair_visual_only_child_change_does_not_rebuild_geometry():
    face = build_human_face("face-01")
    graph = RuntimeGraph.from_component(face)
    service = CachedGeometryGenerator(default_face_geometry_registry(), GeometryCache(max_entries=32))
    first = service.generate(graph, "face-01", generator=EYE_PAIR_GEOMETRY_GENERATOR)
    graph.get("left_eye").component.visual = graph.get("left_eye").component.visual.__class__(fill_color="#ff0000")
    second = service.generate(graph, "face-01", generator=EYE_PAIR_GEOMETRY_GENERATOR)
    assert second.cache_hit is True
    assert second.geometry is first.geometry


def test_face_with_eyes_is_a_real_composite_generator():
    graph = _face_graph()
    service = CachedGeometryGenerator(default_face_geometry_registry(), GeometryCache(max_entries=32))
    result = service.generate(graph, "face-01", generator=FACE_WITH_EYES_GEOMETRY_GENERATOR)
    assert result.geometry.paths
    assert any(s.name == "head:head" for s in result.geometry.surfaces)
    assert any(s.name == "eyes:left_eye:aperture" for s in result.geometry.surfaces)
    assert any(s.name == "eyes:right_eye:aperture" for s in result.geometry.surfaces)


def test_composite_dependency_is_recorded_for_targeted_invalidation():
    graph = _face_graph()
    service = CachedGeometryGenerator(default_face_geometry_registry(), GeometryCache(max_entries=32))
    service.generate(graph, "face-01", generator=FACE_WITH_EYES_GEOMETRY_GENERATOR)
    keys = service.cache.keys()
    target_key = next(k for k in keys if k.generator == FACE_WITH_EYES_GEOMETRY_GENERATOR)
    entry = next(e for e in service.cache._entries.values() if e.key == target_key)  # introspection test only
    assert "left_eye" in entry.dependency_ids
    assert "right_eye" in entry.dependency_ids


def test_declared_generator_dependency_cycle_is_rejected():
    registry = GeometryGeneratorRegistry()
    registry.register(RegisteredGeometryGenerator(
        "cycle.a", "1", ("a",), lambda c, i: GeometryContract(),
        geometry_dependencies_fn=lambda c, i: ("b",),
    ))
    registry.register(RegisteredGeometryGenerator(
        "cycle.b", "1", ("b",), lambda c, i: GeometryContract(),
        geometry_dependencies_fn=lambda c, i: ("a",),
    ))
    a = Component("a", "a")
    b = Component("b", "b")
    # Relation-like cross dependency is declared by the generators; hierarchy is not needed.
    graph = RuntimeGraph.from_component(a)
    # Build a synthetic graph with both nodes via a common root.
    root = Component("root", "root")
    root.add_child(a)
    root.add_child(b)
    graph = RuntimeGraph.from_component(root)
    service = CachedGeometryGenerator(registry, GeometryCache(max_entries=8))
    with pytest.raises(ValueError, match="dependency cycle"):
        service.generate(graph, "a")
