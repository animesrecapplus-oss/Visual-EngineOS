"""Stable identity primitives shared across runtime subsystems.

This module deliberately has no dependency on graph, cache, or resolution modules.
Keeping the digest primitive at this low boundary prevents dependency cycles while
allowing versioning and relation invalidation to use exactly the same canonical identity.
"""

from __future__ import annotations

import hashlib
import json
from typing import Any

from visual_engine.runtime.canonical import canonicalize


def stable_digest(value: Any) -> str:
    """Return the canonical SHA-256 digest for a supported runtime value."""
    encoded = json.dumps(
        canonicalize(value),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
