"""A9 adversarial/property-style regression suite.

These tests intentionally probe failure boundaries rather than happy-path examples:
identity canonicalization, graph topology, cache invalidation, hostile nested data,
and degenerate transforms. The suite is deterministic and does not require Hypothesis
or a live PostgreSQL server, so it can run in the minimal project environment.
"""
from __future__ import annotations

import math
import threading

import pytest

from visual_engine.model import Component, GeometryContract, GeometryPrimitive, LocalTransform, Relation
from visual_engine.runtime.geometry_cache import GeometryCache
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.geometry_transform import transform_geometry_contract
from visual_engine.runtime.versioning import stable_digest


def test_canonicalizer_rejects_mapping_key_aliases_instead_of_stringifying() -> None:
    with pytest.raises(TypeError, match="mapping keys must be strings"):
        stable_digest({1: "numeric", "1": "text"})


def test_canonicalizer_rejects_recursive_list_without_recursion_error() -> None:
    value: list[object] = []
    value.append(value)
    with pytest.raises(ValueError, match="cyclic value"):
        stable_digest(value)


def test_canonicalizer_is_invariant_to_mapping_insertion_order() -> None:
    assert stable_digest({"b": 2, "a": 1}) == stable_digest({"a": 1, "b": 2})


def test_runtime_graph_rejects_object_cycle_before_recursive_walk() -> None:
    root = Component("root", "entity")
    child = Component("child", "part")
    root.children.append(child)
    child.parent_id = root.id
    child.children.append(root)
    # The child points back to the active root while the root retains the valid
    # top-level parent link; this isolates object-cycle detection from parent mismatch.
    root.parent_id = None
    with pytest.raises(ValueError, match="Cycle"):
        RuntimeGraph.from_component(root)


def _relation_graph(order: tuple[str, ...]) -> RuntimeGraph:
    root = Component("root", "entity")
    a = Component("a", "part")
    b = Component("b", "part")
    target = Component("target", "part")
    root.add_child(a)
    root.add_child(b)
    root.add_child(target)
    relations = {
        "a": Relation("a", "DEFORMATION", "target", {"geometry_inputs": {"axis": "x"}}),
        "b": Relation("b", "DEFORMATION", "target", {"geometry_inputs": {"axis": "y"}}),
    }
    for key in order:
        target.relations.append(relations[key])
    return RuntimeGraph.from_component(root)


def test_relation_permutation_does_not_change_geometry_dependency_identity() -> None:
    from visual_engine.runtime.geometry_cache import geometry_dependency_fingerprint

    first = _relation_graph(("a", "b"))
    second = _relation_graph(("b", "a"))
    assert geometry_dependency_fingerprint(first, "target") == geometry_dependency_fingerprint(second, "target")


def test_component_mutation_changes_geometry_input_identity() -> None:
    from visual_engine.runtime.geometry_cache import geometry_input_fingerprint

    component = Component("eye", "eye")
    before = geometry_input_fingerprint(component)
    from visual_engine.model import Parameter
    component.parameters["width"] = Parameter("width", 1.0)
    after = geometry_input_fingerprint(component)
    assert before != after


def test_cache_rejects_invalid_dependency_ids_before_mutating_state() -> None:
    cache = GeometryCache(max_entries=4, max_bytes=None)
    from visual_engine.runtime.geometry_cache import GeometryCacheKey
    from visual_engine.runtime.versioning import VersionStamp

    key = GeometryCacheKey("c", "d", "g", "gen", "1", VersionStamp())
    with pytest.raises(ValueError, match="dependency ids"):
        cache.put(key, GeometryContract(), dependency_ids=("ok", ""))
    assert cache.stats().entries == 0


def test_cache_invalidation_is_idempotent() -> None:
    cache = GeometryCache(max_entries=4, max_bytes=None)
    from visual_engine.runtime.geometry_cache import GeometryCacheKey
    from visual_engine.runtime.versioning import VersionStamp

    key = GeometryCacheKey("c", "d", "g", "gen", "1", VersionStamp())
    cache.put(key, GeometryContract(), dependency_ids=("dep",))
    assert cache.invalidate_component("dep") == 1
    assert cache.invalidate_component("dep") == 0


def test_transform_rejects_noninvertible_matrix_even_when_finite() -> None:
    geometry = GeometryContract(primitives=(GeometryPrimitive("point", {"x": 1.0, "y": 2.0}),))
    with pytest.raises(ValueError, match="invertible"):
        transform_geometry_contract(geometry, ((1.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 1.0)))


def test_local_transform_rejects_nonfinite_and_zero_scales() -> None:
    with pytest.raises(ValueError, match="finite"):
        LocalTransform(rotation_deg=math.inf)
    with pytest.raises(ValueError, match="non-zero"):
        LocalTransform(scale_x=0.0)


def test_geometry_metadata_rejects_cycles_and_non_string_keys() -> None:
    cyclic: dict[str, object] = {}
    cyclic["self"] = cyclic
    with pytest.raises(ValueError, match="cyclic geometry payload"):
        GeometryPrimitive("metadata", cyclic)
    with pytest.raises(TypeError, match="keys must be strings"):
        GeometryPrimitive("metadata", {1: "bad"})


def test_concurrent_same_key_builds_once() -> None:
    cache = GeometryCache(max_entries=4, max_bytes=None)
    from visual_engine.runtime.geometry_cache import GeometryCacheKey
    from visual_engine.runtime.versioning import VersionStamp

    key = GeometryCacheKey("c", "d", "g", "gen", "1", VersionStamp())
    lock = threading.Lock()
    calls = 0

    def builder() -> GeometryContract:
        nonlocal calls
        with lock:
            calls += 1
        return GeometryContract(primitives=(GeometryPrimitive("point", {"x": 1.0, "y": 2.0}),))

    results: list[GeometryContract] = []
    errors: list[BaseException] = []

    def worker() -> None:
        try:
            results.append(cache.get_or_build(key, builder))
        except BaseException as exc:  # pragma: no cover - only exercised on failure
            errors.append(exc)

    threads = [threading.Thread(target=worker) for _ in range(8)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    assert not errors
    assert calls == 1
    assert len(results) == 8


def test_public_facades_remain_import_compatible_after_refactor() -> None:
    from visual_engine.components.face.eyes.core import EyeAppearance, EyeParameters, Gaze, build_eye_geometry
    from visual_engine.components.face.eyes.pair import build_eye_pair
    from visual_engine.render import eye_outer_path, render_eye_pair_svg, render_eye_svg
    from visual_engine.runtime import GeometryCache, geometry_input_fingerprint

    geometry = build_eye_geometry(EyeParameters(), gaze=Gaze())
    assert geometry.nominal_width > 0
    assert eye_outer_path(geometry)
    assert render_eye_svg(geometry).startswith("<svg")
    assert render_eye_pair_svg(build_eye_pair()).startswith("<svg")
    assert GeometryCache is not None
    assert geometry_input_fingerprint(Component("x", "eye"))
