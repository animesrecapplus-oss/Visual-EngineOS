from __future__ import annotations

import pytest
from visual_engine.components.common.geometry_contract import GeometryBounds, GeometryContract, GeometryPrimitive
from visual_engine.runtime.placement import AnchorReference, DimensionConstraint, PlacementIntent, resolve_placed_geometry
from visual_engine.runtime.placement_constraints import (
    ClearanceConstraint, ContainmentConstraint, NonPenetrationConstraint,
    PlacementConstraintSet, resolve_constrained_placement,
)


def rect(x0, y0, x1, y1, anchor=(0.0, 0.0, 0.0)):
    return GeometryContract(
        bounds=GeometryBounds(x0, y0, x1, y1),
        primitives=(GeometryPrimitive("polygon", {"points": ((x0,y0),(x1,y0),(x1,y1),(x0,y1))}),),
        anchors={"origin": anchor},
    )


def intent(src="s", tgt="t"):
    return PlacementIntent(src, tgt, AnchorReference("origin"), AnchorReference("origin"))


def test_containment_constraint_satisfied():
    source = rect(-1, -1, 1, 1)
    target = rect(-5, -5, 5, 5)
    solved = resolve_constrained_placement(source, target, intent(), PlacementConstraintSet(containment=ContainmentConstraint()))
    assert solved.checks[0].status.value == "satisfied"


def test_containment_constraint_rejects_penetration():
    source = rect(-1, -1, 1, 1)
    target = rect(-0.5, -0.5, 0.5, 0.5)
    with pytest.raises(ValueError, match="containment"):
        resolve_constrained_placement(source, target, intent(), PlacementConstraintSet(containment=ContainmentConstraint()))


def test_non_penetration_is_explicit_and_rejects_overlap():
    source = rect(-1, -1, 1, 1)
    target = rect(-0.5, -0.5, 0.5, 0.5)
    with pytest.raises(ValueError, match="non_penetration"):
        resolve_constrained_placement(source, target, intent(), PlacementConstraintSet(non_penetration=NonPenetrationConstraint()))


def test_clearance_is_measured_not_approximated_by_bounds():
    source = rect(0, 0, 1, 1)
    target = rect(2, 0, 3, 1, anchor=(4.0, 0.0, 0.0))
    solved = resolve_constrained_placement(source, target, intent(), PlacementConstraintSet(clearance=ClearanceConstraint(1.0)))
    assert solved.checks[0].measured == pytest.approx(1.0)


def test_resolved_geometry_preserves_frame_and_applies_solution():
    source = rect(-1, -1, 1, 1)
    target = rect(10, 10, 12, 12)
    solved = resolve_constrained_placement(source, target, intent(), PlacementConstraintSet())
    placed = resolve_placed_geometry(source, solved.solution)
    assert placed.coordinate_frame == source.coordinate_frame
    assert placed.anchors["origin"][:2] == pytest.approx((0.0, 0.0))


def test_dimension_plus_constraint_is_still_analytic():
    source = rect(-1, -1, 1, 1)
    target = rect(-5, -5, 5, 5)
    i = PlacementIntent("s", "t", AnchorReference("origin"), AnchorReference("origin"), dimension=DimensionConstraint(width_ratio=0.5, height_ratio=0.5))
    solved = resolve_constrained_placement(source, target, i, PlacementConstraintSet())
    assert solved.solution.scale_x == pytest.approx(2.5)
