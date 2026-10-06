from visual_engine.runtime.version_policy import ENGINE_VERSION, SCHEMA_VERSION


def canonical_entity_record(entity_id: str, root_kind: str, seed: int, engine_version: str = ENGINE_VERSION) -> dict:
    """Build the canonical serialized record using independent engine/schema versions."""
    return {
        "entity_id": entity_id,
        "root_kind": root_kind,
        "seed": seed,
        "engine_version": engine_version,
        "schema_version": SCHEMA_VERSION,
    }
