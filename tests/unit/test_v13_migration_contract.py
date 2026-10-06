from pathlib import Path


def test_state_effect_migration_declares_required_tables_and_constraints():
    sql = Path(__file__).parents[2] / "db" / "migrations" / "007_v1_3_state_effect_precedence.sql"
    text = sql.read_text(encoding="utf-8")
    for token in (
        "CREATE TABLE IF NOT EXISTS component_states",
        "exclusive_group",
        "conflicts JSONB",
        "requires JSONB",
        "CREATE TABLE IF NOT EXISTS visual_effect_definitions",
        "CREATE TABLE IF NOT EXISTS component_effect_bindings",
        "target_component_id TEXT NOT NULL REFERENCES components",
    ):
        assert token in text
