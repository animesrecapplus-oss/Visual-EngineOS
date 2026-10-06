import threading

from visual_engine.model import Component, GeometryContract, GeometryPrimitive, LocalTransform, Parameter, Relation, VisualContract
from visual_engine.runtime import GeometryCache, RuntimeGraph, VersionStamp, geometry_dependency_ids, geometry_input_fingerprint


def _graph():
    root = Component("root", "root")
    arm = Component("arm", "arm")
    hand = Component("hand", "hand", parameters={"pressure": Parameter("pressure", 0.5)})
    face = Component("face", "face")
    unrelated = Component("unrelated", "other")
    root.add_child(arm); arm.add_child(hand); root.add_child(face); root.add_child(unrelated)
    hand.relations.append(Relation("hand", "OCCLUSION", "face"))
    return root


def _geometry(r=2.0):
    return GeometryContract(primitives=(GeometryPrimitive("circle", {"r": r}),))


def test_geometry_input_fingerprint_excludes_visual_and_transform():
    c = Component("eye", "eye")
    before = geometry_input_fingerprint(c)
    c.visual = VisualContract(fill_color="#ff0000")
    c.transform = LocalTransform(x=10, y=4, rotation_deg=30)
    assert geometry_input_fingerprint(c) == before
    c.parameters["width"] = Parameter("width", 2.0)
    assert geometry_input_fingerprint(c) != before


def test_cache_hits_without_rebuilding():
    graph = RuntimeGraph.from_component(_graph())
    cache = GeometryCache(max_entries=10, max_bytes=10000)
    calls = []
    def build(): calls.append(1); return _geometry()
    a = cache.get_or_build_for_graph(graph, "face", build, generator="test.eye", generator_version="1")
    b = cache.get_or_build_for_graph(graph, "face", build, generator="test.eye", generator_version="1")
    assert a is b and calls == [1]
    assert cache.stats().hits == 1 and cache.stats().builds == 1


def test_visual_only_change_does_not_miss_geometry_cache():
    root = Component("root", "root")
    eye = Component("eye", "eye", visual=VisualContract(fill_color="#ffffff"))
    root.add_child(eye); graph = RuntimeGraph.from_component(root)
    cache = GeometryCache(max_entries=10); calls = []
    cache.get_or_build_for_graph(graph, "eye", lambda: calls.append(1) or _geometry(), generator="eye", generator_version="1")
    eye.visual = VisualContract(fill_color="#00ff00")
    graph2 = RuntimeGraph.from_component(root)
    cache.get_or_build_for_graph(graph2, "eye", lambda: calls.append(1) or _geometry(), generator="eye", generator_version="1")
    assert calls == [1]


def test_relation_visual_effect_change_does_not_miss_geometry_cache():
    root = _graph()
    root.find("hand").relations[0].metadata["effect"] = {"kind": "occlusion", "alpha": 0.2}
    graph = RuntimeGraph.from_component(root)
    cache = GeometryCache(max_entries=10); calls = []
    cache.get_or_build_for_graph(graph, "face", lambda: calls.append(1) or _geometry(), generator="face", generator_version="1")
    root.find("hand").relations[0].metadata["effect"]["alpha"] = 0.8
    graph2 = RuntimeGraph.from_component(root)
    cache.get_or_build_for_graph(graph2, "face", lambda: calls.append(1) or _geometry(3), generator="face", generator_version="1")
    assert calls == [1]


def test_relation_geometry_inputs_change_misses_geometry_cache():
    root = _graph()
    root.find("hand").relations[0].metadata["geometry_inputs"] = {"contact_offset": 1.0}
    graph = RuntimeGraph.from_component(root)
    cache = GeometryCache(max_entries=10); calls = []
    cache.get_or_build_for_graph(graph, "face", lambda: calls.append(1) or _geometry(), generator="face", generator_version="1")
    root.find("hand").relations[0].metadata["geometry_inputs"]["contact_offset"] = 2.0
    graph2 = RuntimeGraph.from_component(root)
    cache.get_or_build_for_graph(graph2, "face", lambda: calls.append(1) or _geometry(3), generator="face", generator_version="1")
    assert calls == [1, 1]


def test_relation_topology_change_misses_geometry_cache():
    root = _graph(); graph = RuntimeGraph.from_component(root)
    cache = GeometryCache(max_entries=10); calls = []
    cache.get_or_build_for_graph(graph, "face", lambda: calls.append(1) or _geometry(), generator="face", generator_version="1")
    root.find("unrelated").relations.append(Relation("unrelated", "CONTACT", "face"))
    graph2 = RuntimeGraph.from_component(root)
    cache.get_or_build_for_graph(graph2, "face", lambda: calls.append(1) or _geometry(3), generator="face", generator_version="1")
    assert calls == [1, 1]


def test_relation_dependency_change_misses_geometry_cache():
    root = _graph(); graph = RuntimeGraph.from_component(root)
    cache = GeometryCache(max_entries=10); calls = []
    cache.get_or_build_for_graph(graph, "face", lambda: calls.append(1) or _geometry(), generator="face", generator_version="1")
    root.find("hand").parameters["pressure"] = Parameter("pressure", 0.9)
    graph2 = RuntimeGraph.from_component(root)
    cache.get_or_build_for_graph(graph2, "face", lambda: calls.append(1) or _geometry(3), generator="face", generator_version="1")
    assert calls == [1, 1]


def test_unrelated_sibling_change_preserves_target_geometry_cache():
    root = _graph(); graph = RuntimeGraph.from_component(root)
    cache = GeometryCache(max_entries=10); calls = []
    cache.get_or_build_for_graph(graph, "face", lambda: calls.append(1) or _geometry(), generator="face", generator_version="1")
    root.find("unrelated").transform = LocalTransform(x=99)
    graph2 = RuntimeGraph.from_component(root)
    cache.get_or_build_for_graph(graph2, "face", lambda: calls.append(1) or _geometry(3), generator="face", generator_version="1")
    assert calls == [1]


def test_explicit_invalidation_uses_reverse_dependency_index():
    root = _graph(); graph = RuntimeGraph.from_component(root)
    cache = GeometryCache(max_entries=10)
    cache.get_or_build_for_graph(graph, "face", lambda: _geometry(), generator="face", generator_version="1")
    cache.get_or_build_for_graph(graph, "unrelated", lambda: _geometry(), generator="other", generator_version="1")
    assert cache.invalidate_component("hand") == 1
    assert cache.stats().entries == 1


def test_generator_version_is_cache_boundary():
    graph = RuntimeGraph.from_component(_graph()); cache = GeometryCache(max_entries=10); calls = []
    cache.get_or_build_for_graph(graph, "face", lambda: calls.append(1) or _geometry(), generator="face", generator_version="1")
    cache.get_or_build_for_graph(graph, "face", lambda: calls.append(1) or _geometry(3), generator="face", generator_version="2")
    assert calls == [1, 1]


def test_resolution_version_is_cache_boundary():
    graph = RuntimeGraph.from_component(_graph()); cache = GeometryCache(max_entries=10); calls = []
    cache.get_or_build_for_graph(graph, "face", lambda: calls.append(1) or _geometry(), generator="face", generator_version="1", version=VersionStamp(resolution="3"))
    cache.get_or_build_for_graph(graph, "face", lambda: calls.append(1) or _geometry(3), generator="face", generator_version="1", version=VersionStamp(resolution="4"))
    assert calls == [1, 1]


def test_lru_eviction_is_deterministic():
    root = Component("root", "root"); a = Component("a", "a"); b = Component("b", "b")
    root.add_child(a); root.add_child(b); graph = RuntimeGraph.from_component(root)
    cache = GeometryCache(max_entries=1)
    cache.get_or_build_for_graph(graph, "a", lambda: _geometry(1), generator="a", generator_version="1")
    cache.get_or_build_for_graph(graph, "b", lambda: _geometry(2), generator="b", generator_version="1")
    assert cache.stats().evictions == 1 and len(cache.keys()) == 1 and cache.keys()[0].component_id == "b"


def test_geometry_larger_than_byte_budget_is_not_left_in_cache():
    graph = RuntimeGraph.from_component(_graph())
    geometry = GeometryContract(primitives=(GeometryPrimitive("polyline", {"points": [(i, i) for i in range(100)]}),))
    cache = GeometryCache(max_entries=10, max_bytes=10)
    cache.get_or_build_for_graph(graph, "face", lambda: geometry, generator="face", generator_version="1")
    assert cache.stats().entries == 0 and cache.stats().evictions == 1


def test_builder_failure_is_not_cached_and_waiters_receive_failure():
    graph = RuntimeGraph.from_component(_graph()); cache = GeometryCache(max_entries=10); calls = []
    started = threading.Event(); release = threading.Event(); errors = []
    def build():
        calls.append(1); started.set(); release.wait(timeout=2); raise RuntimeError("boom")
    def worker():
        try: cache.get_or_build_for_graph(graph, "face", build, generator="face", generator_version="1")
        except RuntimeError as exc: errors.append(str(exc))
    t1 = threading.Thread(target=worker); t2 = threading.Thread(target=worker)
    t1.start(); assert started.wait(timeout=2); t2.start(); release.set(); t1.join(); t2.join()
    assert sorted(errors) == ["boom", "boom"] and calls == [1] and cache.stats().entries == 0


def test_concurrent_same_key_builds_once():
    graph = RuntimeGraph.from_component(_graph()); cache = GeometryCache(max_entries=10); calls = []
    started = threading.Event(); release = threading.Event(); results = []; errors = []
    def build():
        calls.append(1); started.set(); release.wait(timeout=2); return _geometry()
    def worker():
        try: results.append(cache.get_or_build_for_graph(graph, "face", build, generator="face", generator_version="1"))
        except BaseException as exc: errors.append(exc)
    t1 = threading.Thread(target=worker); t2 = threading.Thread(target=worker)
    t1.start(); assert started.wait(timeout=2); t2.start(); release.set(); t1.join(); t2.join()
    assert not errors and calls == [1] and len(results) == 2 and results[0] is results[1]


def test_dependency_ids_include_target_ancestors_and_relation_dependency_ancestors():
    graph = RuntimeGraph.from_component(_graph())
    assert geometry_dependency_ids(graph, "face") == ("arm", "face", "hand", "root")


def test_authored_geometry_changes_geometry_input_fingerprint():
    c = Component("eye", "eye", geometry=_geometry(2.0))
    before = geometry_input_fingerprint(c)
    c.geometry = _geometry(3.0)
    assert geometry_input_fingerprint(c) != before


def test_geometry_fingerprint_contract_payload_is_versioned_and_explicit():
    from visual_engine.runtime.geometry_cache import (
        GEOMETRY_FINGERPRINT_ALGORITHM,
        GEOMETRY_FINGERPRINT_CONTRACT_VERSION,
        geometry_input_payload,
    )

    payload = geometry_input_payload(Component("eye", "eye"), {"width": 1.0})
    assert payload["contract_version"] == GEOMETRY_FINGERPRINT_CONTRACT_VERSION == "1"
    assert payload["algorithm"] == GEOMETRY_FINGERPRINT_ALGORITHM == "sha256"
    assert set(payload["component"]) == {"kind", "parameters", "anchors", "constraints", "profiles", "state", "geometry"}
    assert "id" not in payload["component"]


def test_geometry_local_fingerprint_changes_for_every_declared_geometry_input():
    from visual_engine.model import Anchor, Constraint, ConstraintKind, Profile, StateLayer

    base = Component("eye", "eye")
    mutations = [
        lambda c: setattr(c, "kind", "ellipse"),
        lambda c: c.parameters.__setitem__("width", Parameter("width", 2.0)),
        lambda c: c.anchors.__setitem__("center", Anchor("center", 1.0, 2.0, 0.0)),
        lambda c: c.constraints.append(Constraint("limit", ConstraintKind.HARD, "x <= 1")),
        lambda c: c.profiles.__setitem__("morphology", Profile("morphology", {"round": 1.0})),
        lambda c: c.state.append(StateLayer("closed")),
        lambda c: setattr(c, "geometry", _geometry(3.0)),
    ]
    before = geometry_input_fingerprint(base)
    for mutate in mutations:
        candidate = Component("eye", "eye")
        mutate(candidate)
        assert geometry_input_fingerprint(candidate) != before


def test_geometry_local_fingerprint_excludes_non_geometry_component_fields():
    from visual_engine.model import AppearanceLayer

    base = Component("eye", "eye")
    before = geometry_input_fingerprint(base)
    base.appearance.append(AppearanceLayer("paint", {"fill": "#fff"}))
    base.visual = VisualContract(fill_color="#ff0000")
    base.transform = LocalTransform(x=10.0, y=5.0, rotation_deg=20.0)
    assert geometry_input_fingerprint(base) == before


def test_component_id_is_not_local_geometry_identity_but_cache_key_keeps_identity_separate():
    from visual_engine.runtime.geometry_cache import GeometryCache

    left = Component("left", "eye")
    right = Component("right", "eye")
    assert geometry_input_fingerprint(left) == geometry_input_fingerprint(right)
    root = Component("root", "root")
    root.add_child(left)
    root.add_child(right)
    graph = RuntimeGraph.from_component(root)
    cache = GeometryCache(max_entries=10)
    key_left = cache.make_key(graph, "left", generator="eye", generator_version="1")
    key_right = cache.make_key(graph, "right", generator="eye", generator_version="1")
    assert key_left.component_id != key_right.component_id
    assert key_left.cache_identity != key_right.cache_identity


def test_geometry_fingerprint_canonicalizes_mapping_order():
    c = Component("eye", "eye")
    first = geometry_input_fingerprint(c, {"a": 1, "b": (2, 3)})
    second = geometry_input_fingerprint(c, {"b": (2, 3), "a": 1})
    assert first == second


def test_geometry_fingerprint_rejects_non_string_mapping_keys_before_hashing():
    c = Component("eye", "eye")
    try:
        geometry_input_fingerprint(c, {1: "invalid"})
    except TypeError as exc:
        assert "mapping keys must be strings" in str(exc)
    else:
        raise AssertionError("non-string fingerprint mapping key was accepted")


def test_geometry_fingerprint_rejects_non_deterministic_container_types():
    c = Component("eye", "eye")
    try:
        geometry_input_fingerprint(c, {"values": {"a", "b"}})
    except TypeError as exc:
        assert "unsupported geometry fingerprint value" in str(exc)
    else:
        raise AssertionError("set was accepted into geometry fingerprint")


def test_geometry_fingerprint_rejects_cyclic_inputs():
    c = Component("eye", "eye")
    values = []
    values.append(values)
    try:
        geometry_input_fingerprint(c, values)
    except ValueError as exc:
        assert "cyclic geometry fingerprint" in str(exc)
    else:
        raise AssertionError("cyclic fingerprint input was accepted")


def test_geometry_dependency_fingerprint_contract_is_versioned():
    from visual_engine.runtime.geometry_cache import (
        GEOMETRY_FINGERPRINT_ALGORITHM,
        GEOMETRY_FINGERPRINT_CONTRACT_VERSION,
        geometry_dependency_fingerprint,
    )

    root = Component("root", "root")
    eye = Component("eye", "eye")
    root.add_child(eye)
    digest = geometry_dependency_fingerprint(RuntimeGraph.from_component(root), "eye")
    assert isinstance(digest, str) and len(digest) == 64
    assert GEOMETRY_FINGERPRINT_CONTRACT_VERSION == "1"
    assert GEOMETRY_FINGERPRINT_ALGORITHM == "sha256"


def test_geometry_fingerprint_rejects_non_finite_inputs():
    import math

    c = Component("eye", "eye")
    for value in (math.nan, math.inf, -math.inf):
        try:
            geometry_input_fingerprint(c, {"value": value})
        except ValueError as exc:
            assert "non-finite geometry fingerprint value" in str(exc)
        else:
            raise AssertionError("non-finite fingerprint input was accepted")


def test_geometry_fingerprint_contract_version_change_creates_new_identity(monkeypatch):
    import visual_engine.runtime.geometry_cache as geometry_cache

    c = Component("eye", "eye")
    before = geometry_cache.geometry_input_fingerprint(c)
    monkeypatch.setattr(geometry_cache, "GEOMETRY_FINGERPRINT_CONTRACT_VERSION", "2")
    after = geometry_cache.geometry_input_fingerprint(c)
    assert before != after
