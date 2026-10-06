from pathlib import Path

from visual_engine.persistence.migrations import discover_migrations


def test_migrations_are_ordered_and_unique():
    migrations = discover_migrations(Path(__file__).parents[2] / "db" / "migrations")
    assert migrations[0].version == "001_v0_3_initial"
    assert migrations[-1].version == "008_v1_3_relation_dependencies"
    assert [m.version for m in migrations] == sorted(m.version for m in migrations)
    assert len({m.version for m in migrations}) == len(migrations)
    assert all(len(m.checksum) == 64 for m in migrations)


def test_initial_migration_owns_schema_version_table_creation():
    migrations = discover_migrations(Path(__file__).parents[2] / "db" / "migrations")
    assert "CREATE TABLE IF NOT EXISTS schema_versions" in migrations[0].sql


class _FakeCursor:
    def __init__(self, state):
        self.state = state
        self.rows = []

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def execute(self, sql, params=None):
        if sql == self.state.get("fail_sql"):
            raise RuntimeError("simulated migration SQL failure")
        self.state["executed"].append(sql)
        if sql.startswith("SELECT schema_version, checksum FROM schema_versions"):
            self.rows = [(v, c) for v, c in sorted(self.state["applied"].items())]
        elif sql.startswith("SELECT schema_version FROM schema_versions"):
            self.rows = [(v,) for v in sorted(self.state["applied"])]
        elif sql.startswith("INSERT INTO schema_versions"):
            self.state["applied"][params[0]] = params[1]

    def fetchall(self):
        return self.rows

    def fetchone(self):
        return self.rows[0] if self.rows else None


class _FakeConnection:
    def __init__(self, state):
        self.state = state

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def cursor(self):
        return _FakeCursor(self.state)

    def commit(self):
        self.state["commits"] += 1


def test_migration_runner_executes_each_missing_migration_once(tmp_path):
    from visual_engine.persistence.migrations import PostgresMigrationRunner, discover_migrations

    source = Path(__file__).parents[2] / "db" / "migrations"
    state = {"applied": {}, "executed": [], "commits": 0}
    runner = PostgresMigrationRunner(lambda: _FakeConnection(state), source)
    migrations = runner.migrate()
    assert len(migrations) == 8
    assert state["commits"] == 1
    discovered = discover_migrations(source)
    # 001 must itself be executed; merely inserting it into the ledger is forbidden.
    assert discovered[0].sql in state["executed"]
    assert all(m.version in state["applied"] for m in discovered)
    assert runner.migrate() == ()
    assert state["commits"] == 2


def test_migration_runner_refuses_a_gapped_history():
    from visual_engine.persistence.migrations import PostgresMigrationRunner, discover_migrations
    import pytest

    source = Path(__file__).parents[2] / "db" / "migrations"
    migrations = discover_migrations(source)
    state = {
        "applied": {
            migrations[0].version: migrations[0].checksum,
            migrations[2].version: migrations[2].checksum,
        },
        "executed": [],
        "commits": 0,
    }
    runner = PostgresMigrationRunner(lambda: _FakeConnection(state), source)
    with pytest.raises(RuntimeError, match="gap"):
        runner.migrate()


def test_migration_runner_refuses_legacy_checksumless_history():
    from visual_engine.persistence.migrations import PostgresMigrationRunner, discover_migrations
    import pytest

    source = Path(__file__).parents[2] / "db" / "migrations"
    migrations = discover_migrations(source)
    state = {"applied": {migrations[0].version: None}, "executed": [], "commits": 0}
    runner = PostgresMigrationRunner(lambda: _FakeConnection(state), source)
    with pytest.raises(RuntimeError, match="no checksum"):
        runner.migrate()


def test_migration_runner_refuses_checksum_drift():
    from visual_engine.persistence.migrations import PostgresMigrationRunner, discover_migrations
    import pytest

    source = Path(__file__).parents[2] / "db" / "migrations"
    migration = discover_migrations(source)[0]
    state = {"applied": {migration.version: "0" * 64}, "executed": [], "commits": 0}
    runner = PostgresMigrationRunner(lambda: _FakeConnection(state), source)
    with pytest.raises(RuntimeError, match="checksum mismatch"):
        runner.migrate()


def test_migration_ledger_is_not_advanced_before_sql_succeeds():
    from visual_engine.persistence.migrations import PostgresMigrationRunner, discover_migrations
    import pytest

    source = Path(__file__).parents[2] / "db" / "migrations"
    first = discover_migrations(source)[0]
    state = {"applied": {}, "executed": [], "commits": 0, "fail_sql": first.sql}
    runner = PostgresMigrationRunner(lambda: _FakeConnection(state), source)
    with pytest.raises(RuntimeError, match="simulated migration SQL failure"):
        runner.migrate()
    assert first.version not in state["applied"]
    assert not any(sql.startswith("INSERT INTO schema_versions") for sql in state["executed"])


def test_migration_runner_requests_transaction_scoped_advisory_lock():
    from visual_engine.persistence.migrations import PostgresMigrationRunner
    from pathlib import Path

    source = Path(__file__).parents[2] / "db" / "migrations"
    state = {"applied": {}, "executed": [], "commits": 0}
    PostgresMigrationRunner(lambda: _FakeConnection(state), source).migrate()
    assert any(sql.startswith("SELECT pg_advisory_xact_lock") for sql in state["executed"])
