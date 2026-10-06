from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class OcularProfileBundle:
    """Declarative profile bundle returned by one optimized PostgreSQL query."""
    family: str
    name: str
    version: int
    payload: dict[str, Any]


class PostgresOcularCatalog:
    """Cold-path catalog access. Never call this from a renderer or pixel loop."""

    SQL = """
    SELECT family, name, version, payload
    FROM ocular_profile_bundles
    WHERE family = %s AND name = %s AND active = TRUE
    ORDER BY version DESC
    LIMIT 1
    """

    def __init__(self, dsn: str):
        self.dsn = dsn

    def _connect(self):
        try:
            import psycopg
        except ImportError as exc:
            raise RuntimeError("Install visual-engine[postgres] to use PostgreSQL") from exc
        return psycopg.connect(self.dsn)

    def load(self, family: str, name: str) -> OcularProfileBundle | None:
        with self._connect() as conn:
            with conn.cursor() as cur:
                cur.execute(self.SQL, (family, name))
                row = cur.fetchone()
        if row is None:
            return None
        return OcularProfileBundle(row[0], row[1], int(row[2]), dict(row[3]))
