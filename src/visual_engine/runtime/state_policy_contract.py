from __future__ import annotations

"""Immutable value contracts produced and consumed by state-policy resolution.

This module owns only the state activation/decision value objects. Resolution
algorithms remain in ``state_policy`` so the compatibility facade keeps the
historical API without retaining duplicate contract definitions.
"""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class StateActivation:
    """One state candidate with its precedence and dependency metadata."""

    name: str
    source_id: str
    priority: int
    specificity: int
    group: str | None
    conflicts: tuple[str, ...]
    requires: tuple[str, ...]
    source_rank: int

    @property
    def precedence_key(self) -> tuple[int, int, int, str, str]:
        return (self.priority, self.source_rank, self.specificity, self.name, self.source_id)


@dataclass(frozen=True, slots=True)
class StateDecision:
    """Audit record explaining acceptance or rejection of one candidate."""

    candidate: StateActivation
    action: str
    reason: str
