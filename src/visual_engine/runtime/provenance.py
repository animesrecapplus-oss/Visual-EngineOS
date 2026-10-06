from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from typing import Any


@dataclass(frozen=True, slots=True)
class ResolutionStep:
    field: str
    component_id: str
    action: str
    policy: str
    detail: str = ""


@dataclass(frozen=True, slots=True)
class ResolutionProvenance:
    """Deterministic field-level explanation of a resolution result."""

    steps: tuple[ResolutionStep, ...] = ()

    def for_field(self, field: str) -> tuple[ResolutionStep, ...]:
        return tuple(s for s in self.steps if s.field == field)

    def final_source(self, field: str) -> str | None:
        values = self.for_field(field)
        return values[-1].component_id if values else None

    def digest(self) -> str:
        payload = [
            {"field": s.field, "component_id": s.component_id, "action": s.action,
             "policy": s.policy, "detail": s.detail}
            for s in self.steps
        ]
        return hashlib.sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
