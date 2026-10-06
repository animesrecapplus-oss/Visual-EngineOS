from visual_engine.persistence import SCHEMA_VERSION, canonical_entity_record
from visual_engine.runtime.version_policy import ENGINE_VERSION


def test_canonical_record_is_stable_shape():
    record = canonical_entity_record("person_0001", "Human", 42)
    assert record == {
        "entity_id": "person_0001",
        "root_kind": "Human",
        "seed": 42,
        "engine_version": ENGINE_VERSION,
        "schema_version": SCHEMA_VERSION,
    }
