"""Real PostgreSQL persistence gate; enabled only when an explicit DSN is provided."""
import os
import pytest

from visual_engine.persistence import PostgresEntityRepository, canonical_entity_record


@pytest.mark.skipif(not os.getenv("VISUAL_ENGINE_POSTGRES_DSN"), reason="requires VISUAL_ENGINE_POSTGRES_DSN")
def test_postgres_migrate_and_entity_round_trip():
    repo = PostgresEntityRepository(os.environ["VISUAL_ENGINE_POSTGRES_DSN"])
    applied = repo.migrate()
    assert repo.current_schema_version() == "008_v1_3_relation_dependencies"
    assert isinstance(applied, tuple)

    record = canonical_entity_record("integration_pg_entity", "Human", 9876)
    repo.save_entity(record)
    assert repo.load_entity("integration_pg_entity") == record
