import math
from math import isclose

from visual_engine.model import Component, LocalTransform, VisualContract, VisualOverrides, ContourOverride
from visual_engine.model.visual_contract import compose_matrices, identity_matrix, transform_point, matrix_determinant, matrix_is_finite
from visual_engine.runtime import RuntimeGraph, ResolutionContext, resolve_component
from visual_engine.runtime.versioning import (
    VersionStamp, component_fingerprint, dependency_fingerprint, resolution_fingerprint,
    invalidation_reasons,
)


def test_transform_identity_and_point_invariants():
    t = LocalTransform(x=4, y=-3, rotation_deg=37, scale_x=2, scale_y=3)
    m = t.matrix()
    assert compose_matrices(identity_matrix(), m) == m
    assert compose_matrices(m, identity_matrix()) == m
    assert transform_point(m, 0, 0) == (4.0, -3.0)
    assert matrix_is_finite(m)
    assert isclose(matrix_determinant(m), 6.0, rel_tol=1e-12)


def test_transform_full_turn_and_periodicity():
    a = LocalTransform(x=3, y=4, rotation_deg=23, scale_x=-2, scale_y=1.5).matrix()
    b = LocalTransform(x=3, y=4, rotation_deg=383, scale_x=-2, scale_y=1.5).matrix()
    for ra, rb in zip(a, b):
        for va, vb in zip(ra, rb):
            assert isclose(va, vb, abs_tol=1e-12)


def test_transform_composition_is_associative_with_tolerance():
    a = LocalTransform(x=1.2, y=-3.4, rotation_deg=12, scale_x=1.1, scale_y=-.8).matrix()
    b = LocalTransform(x=-2, y=4, rotation_deg=-71, scale_x=.7, scale_y=1.3).matrix()
    c = LocalTransform(x=5, y=2, rotation_deg=180.5, scale_x=-1.2, scale_y=.9).matrix()
    left = compose_matrices(compose_matrices(a, b), c)
    right = compose_matrices(a, compose_matrices(b, c))
    for rl, rr in zip(left, right):
        for vl, vr in zip(rl, rr):
            assert isclose(vl, vr, rel_tol=1e-12, abs_tol=1e-12)


def test_resolution_provenance_explains_each_visual_field():
    root = Component("root", "root", visual=VisualContract(fill_color="#123456", opacity=.8))
    child = Component("child", "child", visual_overrides=VisualOverrides(contour=ContourOverride(width=2), opacity=.5))
    root.add_child(child)
    result = resolve_component(RuntimeGraph.from_component(root), "child")
    for field in ("fill_color", "contour", "material", "opacity", "visibility"):
        assert result.provenance.for_field(field)
    assert result.provenance.for_field("fill_color")[-1].action == "inherit"
    assert result.provenance.for_field("contour")[-1].action == "override"
    assert result.provenance.for_field("opacity")[-1].action == "multiply"
    assert result.provenance.digest() == result.provenance.digest()


def test_resolution_provenance_records_effect_and_transform_policies():
    root = Component("root", "root", transform=LocalTransform(x=2))
    child = Component("child", "child", transform=LocalTransform(x=3))
    root.add_child(child)
    result = resolve_component(RuntimeGraph.from_component(root), "child", context=ResolutionContext(shadow_alpha=.2))
    assert result.provenance.final_source("world_transform") == "child"
    assert result.provenance.final_source("shadow") == "child"


def test_dependency_fingerprint_changes_for_ancestor_but_not_sibling():
    root = Component("root", "root")
    a = Component("a", "child")
    b = Component("b", "child")
    root.add_child(a); root.add_child(b)
    graph = RuntimeGraph.from_component(root)
    before = dependency_fingerprint(graph, "a")
    root.transform = LocalTransform(x=10)
    graph2 = RuntimeGraph.from_component(root)
    assert dependency_fingerprint(graph2, "a") != before
    sibling_before = dependency_fingerprint(graph, "a")
    b.transform = LocalTransform(x=99)
    graph3 = RuntimeGraph.from_component(root)
    assert dependency_fingerprint(graph3, "a") == sibling_before


def test_invalidation_is_ancestor_scoped():
    root = Component("root", "root")
    a = Component("a", "child")
    b = Component("b", "child")
    root.add_child(a); root.add_child(b)
    graph = RuntimeGraph.from_component(root)
    assert invalidation_reasons(graph, "a", "root")
    assert invalidation_reasons(graph, "a", "a")
    assert not invalidation_reasons(graph, "a", "b")


def test_resolution_fingerprint_changes_with_context_and_version():
    root = Component("root", "root")
    graph = RuntimeGraph.from_component(root)
    c1 = ResolutionContext(active_states=("wet",))
    c2 = ResolutionContext(active_states=("dry",))
    f1 = resolution_fingerprint(graph, "root", c1, VersionStamp())
    f2 = resolution_fingerprint(graph, "root", c2, VersionStamp())
    f3 = resolution_fingerprint(graph, "root", c1, VersionStamp(resolution="7"))
    assert f1.cache_identity != f2.cache_identity
    assert f1.cache_identity != f3.cache_identity


def test_resolved_component_exposes_versioned_identity():
    root = Component("root", "root")
    graph = RuntimeGraph.from_component(root)
    version = VersionStamp(engine="1.3.0", schema="1", resolution="7")
    result = resolve_component(graph, "root", version=version)
    assert result.version == version
    assert result.fingerprint is not None
    assert result.fingerprint.version == version
    assert result.fingerprint.component_id == "root"


def test_version_boundary_invalidates_even_when_content_is_identical():
    root = Component("root", "root")
    graph = RuntimeGraph.from_component(root)
    context = ResolutionContext()
    a = resolution_fingerprint(graph, "root", context, VersionStamp(resolution="1"))
    b = resolution_fingerprint(graph, "root", context, VersionStamp(resolution="3"))
    assert not a.is_compatible_with(b)


def test_context_order_is_canonical_for_set_like_state_resolution():
    root = Component("root", "root")
    graph = RuntimeGraph.from_component(root)
    a = resolution_fingerprint(graph, "root", ResolutionContext(active_states=("wet", "cold")))
    b = resolution_fingerprint(graph, "root", ResolutionContext(active_states=("cold", "wet")))
    # Active state names are set-like; context canonicalization makes order irrelevant.
    assert a.cache_identity == b.cache_identity
