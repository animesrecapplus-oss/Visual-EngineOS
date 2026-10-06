import math

import pytest

import visual_engine.runtime as runtime
from visual_engine.runtime import placement as legacy
from visual_engine.runtime import placement_contract as canonical


def test_canonical_owner_and_public_identity_are_unique():
    assert canonical.PlacementIntent is legacy.PlacementIntent is runtime.PlacementIntent
    assert canonical.PlacementSolution is legacy.PlacementSolution is runtime.PlacementSolution
    assert canonical.AnchorReference is runtime.AnchorReference


def test_contracts_are_frozen_and_deterministic():
    intent = canonical.PlacementIntent("source", "target", canonical.AnchorReference("center"), canonical.AnchorReference("center"))
    assert intent.rotation_deg == 0.0
    solution = canonical.PlacementSolution("source", "target", (1.0, 2.0), 15.0, 2.0, 3.0, 1.0, (0.0, 0.0, 0.0), (1.0, 1.0, 0.0), diagnostics={"z": 2.0, "a": "stable"})
    assert tuple(solution.diagnostics) == ("a", "z")
    with pytest.raises((AttributeError, TypeError)):
        solution.scale_x = 4.0


def test_hostile_numeric_and_conflicting_states_are_rejected():
    ref = canonical.AnchorReference("center")
    for value in (math.nan, math.inf, -math.inf):
        with pytest.raises(ValueError):
            canonical.PlacementIntent("s", "t", ref, ref, rotation_deg=value)
    with pytest.raises(ValueError):
        canonical.DimensionConstraint(width_ratio=0.0)
    with pytest.raises(ValueError):
        canonical.PlacementIntent("s", "t", ref, ref, depth_relation=canonical.PlacementDepthRelation.COPLANAR, depth_offset=1.0)


def test_solution_transform_rejects_non_finite_points():
    solution = canonical.PlacementSolution("s", "t", (1.0, 2.0), 0.0, 2.0, 2.0, 1.0, (0.0, 0.0, 0.0), (1.0, 1.0, 0.0))
    assert solution.transform_point(1.0, 2.0) == (3.0, 6.0)
    with pytest.raises(ValueError):
        solution.transform_point(math.nan, 2.0)
