from __future__ import annotations

"""Immutable value contracts for explicit placement constraints.

This module owns only the constraint vocabulary and result contracts. It does
not resolve placement or materialize geometry; those algorithms stay in the
compatibility/resolution module.
"""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import TYPE_CHECKING, Mapping

if TYPE_CHECKING:
    from visual_engine.runtime.placement_contract import PlacementSolution


class ConstraintStatus(str, Enum):
    SATISFIED = "satisfied"
    VIOLATED = "violated"


@dataclass(frozen=True, slots=True)
class ContainmentConstraint:
    """Require the placed source region to be contained in the target region."""
    tolerance: float = 1e-9

    def __post_init__(self) -> None:
        if not math.isfinite(self.tolerance) or self.tolerance < 0:
            raise ValueError("containment tolerance must be finite and >= 0")


@dataclass(frozen=True, slots=True)
class ClearanceConstraint:
    """Require a minimum boundary distance between source and target."""
    minimum_distance: float
    tolerance: float = 1e-9

    def __post_init__(self) -> None:
        if not math.isfinite(self.minimum_distance) or self.minimum_distance < 0:
            raise ValueError("minimum_distance must be finite and >= 0")
        if not math.isfinite(self.tolerance) or self.tolerance < 0:
            raise ValueError("clearance tolerance must be finite and >= 0")


@dataclass(frozen=True, slots=True)
class NonPenetrationConstraint:
    """Require two placed regions not to overlap in area."""
    tolerance: float = 1e-9

    def __post_init__(self) -> None:
        if not math.isfinite(self.tolerance) or self.tolerance < 0:
            raise ValueError("penetration tolerance must be finite and >= 0")


@dataclass(frozen=True, slots=True)
class PlacementConstraintSet:
    """Hard geometric constraints evaluated after analytic placement resolution."""
    containment: ContainmentConstraint | None = None
    clearance: ClearanceConstraint | None = None
    non_penetration: NonPenetrationConstraint | None = None
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "metadata", dict(sorted((self.metadata or {}).items())))


@dataclass(frozen=True, slots=True)
class ConstraintCheck:
    name: str
    status: ConstraintStatus
    measured: float
    limit: float
    message: str


@dataclass(frozen=True, slots=True)
class ConstrainedPlacementSolution:
    solution: "PlacementSolution"
    checks: tuple[ConstraintCheck, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "checks", tuple(sorted(self.checks, key=lambda c: c.name)))
        if any(c.status is ConstraintStatus.VIOLATED for c in self.checks):
            raise ValueError("ConstrainedPlacementSolution cannot contain violated constraints")
