from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Any


@dataclass(frozen=True, slots=True)
class Migration:
    version: str
    path: Path
    sql: str

    @property
    def checksum(self) -> str:
        """Return the immutable SHA-256 identity of the exact migration payload."""
        return hashlib.sha256(self.sql.encode("utf-8")).hexdigest()


def discover_migrations(directory: str | Path | None = None) -> tuple[Migration, ...]:
    """Discover ordered SQL migrations without guessing database state."""
    base = Path(directory) if directory is not None else Path(__file__).resolve().parents[3] / "db" / "migrations"
    if not base.is_dir():
        raise FileNotFoundError(f"Migration directory does not exist: {base}")
    files = sorted(base.glob("*.sql"))
    migrations = tuple(Migration(path.stem, path, path.read_text(encoding="utf-8")) for path in files)
    if not migrations:
        raise RuntimeError(f"No SQL migrations found in {base}")
    versions = [m.version for m in migrations]
    if len(set(versions)) != len(versions):
        raise RuntimeError("Duplicate migration versions detected")
    return migrations


class PostgresMigrationRunner:
    """Apply repository migrations transactionally and record their exact checksums.

    The migration ledger is deliberately stricter than a simple "latest version" marker:
    an already-applied migration must have the same SQL checksum, and a later migration
    cannot be present while an earlier one is missing.  This prevents silent schema drift.
    """

    # One transaction-scoped advisory lock serializes migration runners connected to the
    # same PostgreSQL database without introducing an application-level lock table.
    _ADVISORY_LOCK_KEY = 781349217

    def __init__(self, connect: Any, directory: str | Path | None = None):
        self._connect_factory = connect
        self.directory = directory

    @staticmethod
    def _ensure_ledger(cur: Any) -> None:
        """Create/upgrade the tiny migration ledger before running application DDL.

        ``ALTER ... IF NOT EXISTS`` keeps databases created by the older checkpoint
        readable while refusing to pretend that their old, checksum-less history was
        cryptographically verified.
        """
        cur.execute(
            "CREATE TABLE IF NOT EXISTS schema_versions ("
            "schema_version TEXT PRIMARY KEY, "
            "applied_at TIMESTAMPTZ NOT NULL DEFAULT now()"
            ")"
        )
        cur.execute(
            "ALTER TABLE schema_versions "
            "ADD COLUMN IF NOT EXISTS checksum TEXT"
        )

    def migrate(self) -> tuple[str, ...]:
        migrations = discover_migrations(self.directory)
        ordered_versions = [m.version for m in migrations]
        known_versions = set(ordered_versions)

        with self._connect_factory() as conn:
            with conn.cursor() as cur:
                # PostgreSQL holds this lock only until transaction end. Two application
                # processes can therefore safely race on startup without interleaving DDL.
                cur.execute("SELECT pg_advisory_xact_lock(%s)", (self._ADVISORY_LOCK_KEY,))
                self._ensure_ledger(cur)
                cur.execute("SELECT schema_version, checksum FROM schema_versions")
                applied_rows = {row[0]: row[1] for row in cur.fetchall()}

                unknown_applied = set(applied_rows) - known_versions
                if unknown_applied:
                    raise RuntimeError(
                        f"Database contains unknown migration versions: {sorted(unknown_applied)}"
                    )

                # A later migration without every predecessor is unsafe. Do this check
                # before executing anything so a bad history cannot be partially advanced.
                first_missing = next(
                    (i for i, version in enumerate(ordered_versions) if version not in applied_rows),
                    None,
                )
                if first_missing is not None and any(
                    version in applied_rows for version in ordered_versions[first_missing + 1 :]
                ):
                    raise RuntimeError(
                        "Database migration history has a gap; refusing to apply out of order"
                    )

                applied_now: list[str] = []
                for migration in migrations:
                    recorded_checksum = applied_rows.get(migration.version)
                    if migration.version in applied_rows:
                        if recorded_checksum is None:
                            # We cannot reconstruct which SQL created an old ledger row.
                            # Refuse to bless it automatically; an operator must verify or
                            # rebuild that database instead of receiving a false PASS.
                            raise RuntimeError(
                                f"Migration {migration.version} has no checksum; "
                                "legacy migration history requires explicit verification"
                            )
                        if recorded_checksum != migration.checksum:
                            raise RuntimeError(
                                f"Migration checksum mismatch for {migration.version}: "
                                f"database={recorded_checksum}, repository={migration.checksum}"
                            )
                        continue

                    # Every missing migration, including 001, must execute its DDL/data.
                    # The previous checkpoint incorrectly recorded 001 without executing it.
                    cur.execute(migration.sql)
                    cur.execute(
                        "INSERT INTO schema_versions(schema_version, checksum) "
                        "VALUES (%s, %s)",
                        (migration.version, migration.checksum),
                    )
                    applied_now.append(migration.version)

            conn.commit()
        return tuple(applied_now)

    def current_version(self) -> str | None:
        """Return the latest repository-known version, not arbitrary lexical DB state."""
        migrations = discover_migrations(self.directory)
        known = {m.version for m in migrations}
        with self._connect_factory() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT schema_version FROM schema_versions")
                applied = {row[0] for row in cur.fetchall()}
        unknown = applied - known
        if unknown:
            raise RuntimeError(f"Database contains unknown migration versions: {sorted(unknown)}")
        for migration in reversed(migrations):
            if migration.version in applied:
                return migration.version
        return None
