"""Canonical cross-surface version policy for the current V1.x engine.

The engine deliberately has several version boundaries with different ownership:
- ENGINE_VERSION identifies executable/package behavior;
- SCHEMA_VERSION identifies the serialized entity schema;
- RESOLUTION_VERSION identifies resolution semantics and therefore cache identity.

These are not interchangeable.  In particular, PostgreSQL migration IDs remain a
separate ordered ledger because a migration is an operation, not the serialized
schema's semantic version.
"""

from __future__ import annotations

from dataclasses import dataclass

# Keep these constants in one runtime-owned policy module.  Packaging metadata is
# checked against ENGINE_VERSION by the A6 verifier so a second literal cannot drift
# silently outside Python source control.
ENGINE_VERSION = "1.3.8"
SCHEMA_VERSION = "2"
RESOLUTION_VERSION = "20"


@dataclass(frozen=True, slots=True)
class VersionPolicy:
    """Immutable view of the three independent version boundaries."""

    engine: str = ENGINE_VERSION
    schema: str = SCHEMA_VERSION
    resolution: str = RESOLUTION_VERSION


CURRENT_VERSION_POLICY = VersionPolicy()
