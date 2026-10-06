from __future__ import annotations

import json
from pathlib import Path

from visual_engine.model import (
    AppearanceLayer, Anchor, Component, Constraint, ConstraintKind, GeometryContract,
    GeometryPath, LocalTransform, Parameter, Profile, Relation, StateLayer,
)
from visual_engine.persistence.serialization import component_from_payload, component_payload, parameter_payload


def _rich_component() -> Component:
    component = Component(
        "eye.left", "Eye",
        transform=LocalTransform(10, 20, 12, 1.2, 0.8, 3),
        geometry=GeometryContract(paths=(GeometryPath((("M", (0, 0)), ("L", (10, 5)), ("Z", ()))),)),
    )
    component.set_parameter(Parameter("width", 12.5, 0, 100))
    component.anchors["canthus"] = Anchor("canthus", 1, 2, 0)
    component.add_constraint(Constraint("ratio", ConstraintKind.HARD, "width/height>0"))
    component.profiles["anime"] = Profile("anime", {"density": 0.8})
    component.add_appearance(AppearanceLayer("base", {"tone": "warm"}, 0.9))
    component.add_state(StateLayer("closed", {"aperture": 0}, priority=10, group="lid"))
    return component


def test_component_contract_payload_round_trips_all_nonrelational_fields():
    original = _rich_component()
    payload = component_payload(original, child_order=7)
    restored = component_from_payload(
        original.id,
        original.kind,
        original.parent_id,
        parameter_payload(original.parameters),
        {name: {"x": a.x, "y": a.y, "z": a.z} for name, a in original.anchors.items()},
        payload,
    )
    assert restored.transform == original.transform
    assert restored.visual == original.visual
    assert restored.visual_overrides == original.visual_overrides
    assert restored.geometry == original.geometry
    assert restored.parameters == original.parameters
    assert restored.anchors == original.anchors


def test_a7_repository_uses_bounded_queries_and_atomic_transaction():
    text = Path(__file__).parents[2].joinpath("src/visual_engine/persistence/postgres.py").read_text(encoding="utf-8")
    assert "with self._connect() as conn:" in text
    assert "conn.commit()" in text
    assert "entity_versions" in text
    assert "component_states" in text
    assert "relations" in text
    assert "WHERE entity_id=%s" in text
    assert "FOR UPDATE" in text
    assert "ANY(%s)" in text
    assert "N+1" in text


def test_a7_does_not_use_per_component_database_queries_for_hydration():
    text = Path(__file__).parents[2].joinpath("src/visual_engine/persistence/postgres.py").read_text(encoding="utf-8")
    load_body = text.split("class PostgresEntityRepository", 1)[1].split("    def load_component_tree", 1)[1]
    # Hydration is intentionally one query per relation family, not one query per component.
    assert load_body.count('cur.execute(') <= 8
    assert "for cid, name, kind, expression, weight in constraint_rows" in load_body
    assert "for cid, _profile_type, name, values in profile_rows" in load_body


def test_parameter_payload_is_json_serializable_and_deterministic():
    component = _rich_component()
    first = json.dumps(parameter_payload(component.parameters), sort_keys=True, separators=(",", ":"))
    second = json.dumps(parameter_payload(component.parameters), sort_keys=True, separators=(",", ":"))
    assert first == second


def test_a7_json_encoding_is_fail_closed_for_non_json_values():
    from visual_engine.persistence.postgres import _json
    try:
        _json({"bad": float("nan")})
    except ValueError:
        pass
    else:
        raise AssertionError("JSONB payload encoding must reject NaN")

    class Unsupported:
        pass

    try:
        _json({"bad": Unsupported()})
    except TypeError:
        pass
    else:
        raise AssertionError("JSONB payload encoding must reject unsupported Python objects")


def test_save_component_tree_rejects_invalid_topology_before_opening_database():
    from visual_engine.persistence import PostgresEntityRepository

    repo = PostgresEntityRepository("postgresql://unused")
    repo._connect = lambda: (_ for _ in ()).throw(AssertionError("database must not be opened"))
    root = Component("root", "Human")
    child = Component("child", "Eye")
    root.add_child(child)
    child.children.append(root)
    root.parent_id = child.id
    record = {"entity_id": "e", "root_kind": "Human", "seed": 1, "engine_version": "1.3.5", "schema_version": "2"}
    import pytest
    with pytest.raises(ValueError, match="Cycle|Parent link"):
        repo.save_component_tree(record, root)
