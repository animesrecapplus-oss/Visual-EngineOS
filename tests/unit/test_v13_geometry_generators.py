import pytest

from visual_engine.components.face.eyes import (
    EyelidAppearance,
    EYE_GEOMETRY_GENERATOR,
    EyeAppearance,
    EyeGeometryInputs,
    EyeParameters,
    Gaze,
    PupilSpec,
    default_eye_geometry_registry,
)
from visual_engine.model import Component, GeometryContract
from visual_engine.runtime import CachedGeometryGenerator, GeometryCache, GeometryGeneratorRegistry, RegisteredGeometryGenerator, RuntimeGraph


def _eye_graph():
    return RuntimeGraph.from_component(Component("eye-01", "eye"))


def test_registry_resolves_eye_default_generator():
    registry = default_eye_geometry_registry()
    assert registry.names() == (EYE_GEOMETRY_GENERATOR,)
    assert registry.defaults() == {"eye": EYE_GEOMETRY_GENERATOR}
    assert registry.for_component(_eye_graph().get("eye-01").component).name == EYE_GEOMETRY_GENERATOR


def test_registry_rejects_duplicate_default_kind():
    registry = GeometryGeneratorRegistry()
    registry.register(RegisteredGeometryGenerator("a", "1", ("eye",), lambda c, i: GeometryContract()))
    with pytest.raises(ValueError):
        registry.register(RegisteredGeometryGenerator("b", "1", ("eye",), lambda c, i: GeometryContract()))


def test_registry_rejects_explicit_generator_for_wrong_kind():
    registry = default_eye_geometry_registry()
    graph = RuntimeGraph.from_component(Component("head", "head"))
    with pytest.raises(ValueError):
        registry.generate(graph.get("head").component, generator=EYE_GEOMETRY_GENERATOR)


def test_eye_generator_returns_renderer_neutral_geometry_contract():
    registry = default_eye_geometry_registry()
    component = _eye_graph().get("eye-01").component
    geometry = registry.generate(component, EyeGeometryInputs(parameters=EyeParameters(width=2.0, height=1.0)))
    assert isinstance(geometry, GeometryContract)
    assert geometry.coordinate_frame == "component"
    assert any(p.data["role"] == "iris" for p in geometry.primitives)
    assert any(p.data["role"] == "pupil" for p in geometry.primitives)
    assert geometry.paths and geometry.paths[0].commands[-1][0] == "Z"


def test_eye_geometry_cache_is_reused_by_registry_entry_point():
    graph = _eye_graph()
    registry = default_eye_geometry_registry()
    service = CachedGeometryGenerator(registry, GeometryCache(max_entries=8))
    inputs = EyeGeometryInputs(parameters=EyeParameters(width=2.0, height=1.0), gaze=Gaze(direction="right"))
    first = service.generate(graph, "eye-01", inputs=inputs)
    second = service.generate(graph, "eye-01", inputs=inputs)
    assert first.cache_hit is False
    assert second.cache_hit is True
    assert first.geometry is second.geometry
    assert first.key == second.key
    assert service.cache.stats().builds == 1


def test_eye_visual_only_changes_do_not_rebuild_geometry():
    graph = _eye_graph()
    registry = default_eye_geometry_registry()
    service = CachedGeometryGenerator(registry, GeometryCache(max_entries=8))
    base = EyeGeometryInputs()
    visual = EyeAppearance(sclera="#ffeeee", outline="#ff0000")
    first = service.generate(graph, "eye-01", inputs=base)
    second = service.generate(graph, "eye-01", inputs=EyeGeometryInputs(appearance=visual))
    assert second.cache_hit is True
    assert first.geometry is second.geometry
    assert service.cache.stats().builds == 1


def test_eye_geometry_relevant_pupil_shape_changes_cache_key():
    graph = _eye_graph()
    registry = default_eye_geometry_registry()
    service = CachedGeometryGenerator(registry, GeometryCache(max_entries=8))
    a = EyeGeometryInputs(appearance=EyeAppearance(pupils=(PupilSpec(shape="ellipse"),)))
    b = EyeGeometryInputs(appearance=EyeAppearance(pupils=(PupilSpec(shape="circle"),)))
    first = service.generate(graph, "eye-01", inputs=a)
    second = service.generate(graph, "eye-01", inputs=b)
    assert second.cache_hit is False
    assert first.key != second.key
    assert service.cache.stats().builds == 2


def test_eye_geometry_cache_changes_when_gaze_changes():
    graph = _eye_graph()
    service = CachedGeometryGenerator(default_eye_geometry_registry(), GeometryCache(max_entries=8))
    a = service.generate(graph, "eye-01", inputs=EyeGeometryInputs(gaze=Gaze(direction="left")))
    b = service.generate(graph, "eye-01", inputs=EyeGeometryInputs(gaze=Gaze(direction="right")))
    assert a.geometry is not b.geometry
    assert a.key.geometry_input_digest != b.key.geometry_input_digest


def test_generator_cache_projection_does_not_drop_geometric_eyelid_inputs():
    graph = _eye_graph()
    service = CachedGeometryGenerator(default_eye_geometry_registry(), GeometryCache(max_entries=8))
    a = EyeGeometryInputs(appearance=EyeAppearance())
    b = EyeGeometryInputs(appearance=EyeAppearance(eyelid=EyelidAppearance(upper_crease_offset=0.20)))
    first = service.generate(graph, "eye-01", inputs=a)
    second = service.generate(graph, "eye-01", inputs=b)
    assert first.key.geometry_input_digest != second.key.geometry_input_digest
