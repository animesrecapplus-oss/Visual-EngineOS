"""Deterministic, fail-closed canonicalization for engine identities.

This module deliberately accepts a small JSON-like value domain. Cache keys,
resolution fingerprints and persistence identities must never depend on Python
object repr(), hash randomization, insertion order of non-semantic containers,
or accidental coercion of colliding mapping keys.
"""
from __future__ import annotations

from dataclasses import fields, is_dataclass
from enum import Enum
import math
from typing import Any


def canonicalize(value: Any, *, _path: str = "value", _active: set[int] | None = None) -> Any:
    """Convert a supported value to deterministic JSON-compatible data.

    Cycles are rejected at the recursion boundary rather than allowed to reach
    ``json.dumps`` as a late ``RecursionError``. Mapping keys must already be
    strings: coercing arbitrary keys to strings can make distinct inputs collide.
    """
    active = _active if _active is not None else set()

    if value is None or isinstance(value, (bool, str, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError(f"non-finite value cannot be fingerprinted at {_path}")
        return value
    if isinstance(value, Enum):
        return canonicalize(value.value, _path=f"{_path}.value", _active=active)

    marker = id(value)
    if marker in active:
        raise ValueError(f"cyclic value cannot be fingerprinted at {_path}")

    if is_dataclass(value) and not isinstance(value, type):
        active.add(marker)
        try:
            return {
                field.name: canonicalize(
                    getattr(value, field.name),
                    _path=f"{_path}.{field.name}",
                    _active=active,
                )
                for field in fields(value)
            }
        finally:
            active.remove(marker)

    if isinstance(value, dict):
        active.add(marker)
        try:
            result: dict[str, Any] = {}
            for key, item in value.items():
                if not isinstance(key, str):
                    raise TypeError(
                        f"mapping keys must be strings for deterministic identity at {_path}; "
                        f"got {type(key).__name__}"
                    )
                if key in result:
                    # Defensive guard; normal Python dict construction cannot
                    # contain duplicate equal keys, but custom Mapping-like
                    # inputs must never be allowed to collapse silently.
                    raise ValueError(f"duplicate canonical mapping key at {_path}.{key}")
                result[key] = canonicalize(item, _path=f"{_path}.{key}", _active=active)
            return {key: result[key] for key in sorted(result)}
        finally:
            active.remove(marker)

    if isinstance(value, (list, tuple)):
        active.add(marker)
        try:
            return [
                canonicalize(item, _path=f"{_path}[{index}]", _active=active)
                for index, item in enumerate(value)
            ]
        finally:
            active.remove(marker)

    raise TypeError(
        f"unsupported value cannot be fingerprinted at {_path}: {type(value).__name__}"
    )
