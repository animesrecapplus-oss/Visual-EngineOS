from __future__ import annotations

import math

import pytest

from visual_engine.runtime import (
    ClearanceConstraint,
    ConstraintStatus,
    ContainmentConstraint,
    ConstrainedPlacementSolution,
    NonPenetrationConstraint,
    PlacementConstraintSet,
)
from visual_engine.runtime.placement_constraints import (
    ClearanceConstraint as LegacyClearanceConstraint,
    ContainmentConstraint as LegacyContainmentConstraint,
    NonPenetrationConstraint as LegacyNonPenetrationConstraint,
    PlacementConstraintSet as LegacyPlacementConstraintSet,
)
from visual_engine.runtime.placement_constraints_contract import (
    ClearanceConstraint as CanonicalClearanceConstraint,
    ContainmentConstraint as CanonicalContainmentConstraint,
    NonPenetrationConstraint as CanonicalNonPenetrationConstraint,
    PlacementConstraintSet as CanonicalPlacementConstraintSet,
)


def test_canonical_owner_and_public_identity() -> None:
    assert ContainmentConstraint is CanonicalContainmentConstraint is LegacyContainmentConstraint
    assert ClearanceConstraint is CanonicalClearanceConstraint is LegacyClearanceConstraint
    assert NonPenetrationConstraint is CanonicalNonPenetrationConstraint is LegacyNonPenetrationConstraint
    assert PlacementConstraintSet is CanonicalPlacementConstraintSet is LegacyPlacementConstraintSet


def test_contracts_are_frozen_and_metadata_is_deterministic() -> None:
    value = PlacementConstraintSet(metadata={"z": "2", "a": "1"})
    assert tuple(value.metadata.items()) == (("a", "1"), ("z", "2"))
    with pytest.raises((AttributeError, TypeError)):
        value.containment = ContainmentConstraint()  # type: ignore[misc]


def test_non_finite_and_negative_values_fail_closed() -> None:
    for value in (math.nan, math.inf, -math.inf, -1.0):
        with pytest.raises(ValueError):
            ContainmentConstraint(tolerance=value)
        with pytest.raises(ValueError):
            NonPenetrationConstraint(tolerance=value)
        with pytest.raises(ValueError):
            ClearanceConstraint(minimum_distance=value)
    with pytest.raises(ValueError):
        ClearanceConstraint(minimum_distance=1.0, tolerance=math.nan)
    with pytest.raises(TypeError):
        ContainmentConstraint(tolerance="bad")  # type: ignore[arg-type]


def test_solution_rejects_violated_checks_and_orders_checks() -> None:
    from unittest.mock import Mock

    from visual_engine.runtime.placement_constraints_contract import ConstraintCheck

    checks = (
        ConstraintCheck("b", ConstraintStatus.SATISFIED, 0.0, 0.0, "ok"),
        ConstraintCheck("a", ConstraintStatus.SATISFIED, 0.0, 0.0, "ok"),
    )
    result = ConstrainedPlacementSolution(Mock(), checks)  # type: ignore[arg-type]
    assert [check.name for check in result.checks] == ["a", "b"]

    violated = ConstraintCheck("a", ConstraintStatus.VIOLATED, 1.0, 0.0, "bad")
    with pytest.raises(ValueError):
        ConstrainedPlacementSolution(Mock(), (violated,))  # type: ignore[arg-type]
