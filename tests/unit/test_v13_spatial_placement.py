import math

import pytest

from visual_engine.components.common.geometry_contract import GeometryBounds, GeometryContract, GeometryPrimitive
from visual_engine.runtime.placement import (
    AnchorReference,
    CoverageIntent,
    DimensionConstraint,
    PlacementDepthRelation,
    PlacementIntent,
    PlacementScaleMode,
    resolve_placement,
)


def rect(x0, y0, x1, y1, *, anchors):
    return GeometryContract(
        bounds=GeometryBounds(x0, y0, x1, y1),
        primitives=(GeometryPrimitive("polygon", {"points": ((x0,y0),(x1,y0),(x1,y1),(x0,y1))}),),
        anchors=anchors,
    )


def test_anchor_alignment_respects_scale_and_rotation():
    source = rect(0, 0, 2, 2, anchors={"center": (1, 1, 0)})
    target = rect(10, 20, 20, 30, anchors={"center": (15, 25, 0)})
    solution = resolve_placement(source, target, PlacementIntent(
        "source", "target", AnchorReference("center"), AnchorReference("center"),
        rotation_deg=90, scale_mode=PlacementScaleMode.UNIFORM,
        dimension=DimensionConstraint(width_ratio=0.4, height_ratio=0.4),
    ))
    assert solution.scale_x == pytest.approx(2.0)
    assert solution.scale_y == pytest.approx(2.0)
    # R*S*(1,1) = (-2,2), so translation maps it to (15,25).
    assert solution.translation == pytest.approx((17.0, 23.0))
    assert solution.transform_point(1, 1) == pytest.approx((15.0, 25.0))


def test_relative_dimensions_are_target_relative_not_pixel_constants():
    source = rect(0, 0, 2, 4, anchors={"center": (1, 2, 0)})
    target = rect(0, 0, 100, 50, anchors={"center": (50, 25, 0)})
    solution = resolve_placement(source, target, PlacementIntent(
        "s", "t", AnchorReference("center"), AnchorReference("center"),
        dimension=DimensionConstraint(width_ratio=0.5),
    ))
    assert solution.scale_x == pytest.approx(25.0)
    assert solution.scale_y == pytest.approx(25.0)


def test_non_uniform_dimension_constraints_can_set_both_axes():
    source = rect(0, 0, 2, 4, anchors={"center": (1, 2, 0)})
    target = rect(0, 0, 100, 50, anchors={"center": (50, 25, 0)})
    solution = resolve_placement(source, target, PlacementIntent(
        "s", "t", AnchorReference("center"), AnchorReference("center"),
        scale_mode=PlacementScaleMode.NON_UNIFORM,
        dimension=DimensionConstraint(width_ratio=0.5, height_ratio=0.25),
    ))
    assert solution.scale_x == pytest.approx(25.0)
    assert solution.scale_y == pytest.approx(3.125)


def test_uniform_dimension_constraints_reject_inconsistent_axes():
    source = rect(0, 0, 2, 4, anchors={"center": (1, 2, 0)})
    target = rect(0, 0, 100, 50, anchors={"center": (50, 25, 0)})
    with pytest.raises(ValueError, match="inconsistent"):
        resolve_placement(source, target, PlacementIntent(
            "s", "t", AnchorReference("center"), AnchorReference("center"),
            dimension=DimensionConstraint(width_ratio=0.5, height_ratio=0.25),
        ))


def test_coverage_intent_solves_geometric_target_fraction():
    source = rect(0, 0, 2, 2, anchors={"center": (1, 1, 0)})
    target = rect(0, 0, 4, 4, anchors={"center": (2, 2, 0)})
    solution = resolve_placement(source, target, PlacementIntent(
        "source", "target", AnchorReference("center"), AnchorReference("center"),
        coverage=CoverageIntent(0.25, tolerance=1e-5),
    ))
    assert solution.scale_x == pytest.approx(1.0, rel=1e-4)
    assert solution.resolved_target_fraction == pytest.approx(0.25, abs=1e-5)
    assert solution.coverage_error <= 1e-5


def test_coverage_requires_source_anchor_inside_source_geometry():
    source = rect(0, 0, 2, 2, anchors={"outside": (10, 10, 0)})
    target = rect(0, 0, 4, 4, anchors={"center": (2, 2, 0)})
    with pytest.raises(ValueError, match="inside source geometry"):
        resolve_placement(source, target, PlacementIntent(
            "s", "t", AnchorReference("outside"), AnchorReference("center"),
            coverage=CoverageIntent(0.25),
        ))


def test_dimension_and_coverage_are_not_implicitly_prioritized():
    source = rect(0, 0, 2, 2, anchors={"center": (1, 1, 0)})
    target = rect(0, 0, 4, 4, anchors={"center": (2, 2, 0)})
    with pytest.raises(ValueError, match="mutually exclusive"):
        resolve_placement(source, target, PlacementIntent(
            "s", "t", AnchorReference("center"), AnchorReference("center"),
            dimension=DimensionConstraint(width_ratio=0.5),
            coverage=CoverageIntent(0.25),
        ))


def test_relative_dimension_is_scale_invariant_under_global_scene_size():
    source_small = rect(0, 0, 2, 2, anchors={"center": (1, 1, 0)})
    target_small = rect(0, 0, 10, 10, anchors={"center": (5, 5, 0)})
    source_large = rect(0, 0, 20, 20, anchors={"center": (10, 10, 0)})
    target_large = rect(0, 0, 100, 100, anchors={"center": (50, 50, 0)})
    intent = lambda sid, tid: PlacementIntent(
        sid, tid, AnchorReference("center"), AnchorReference("center"),
        dimension=DimensionConstraint(width_ratio=0.4, height_ratio=0.4),
    )
    a = resolve_placement(source_small, target_small, intent("s1", "t1"))
    b = resolve_placement(source_large, target_large, intent("s2", "t2"))
    assert a.scale_x / b.scale_x == pytest.approx(1.0)
    assert a.scale_y / b.scale_y == pytest.approx(1.0)


def test_coverage_requires_target_anchor_inside_target_geometry():
    source = rect(0, 0, 2, 2, anchors={"center": (1, 1, 0)})
    target = rect(0, 0, 4, 4, anchors={"outside": (20, 20, 0)})
    with pytest.raises(ValueError, match="target_anchor inside target geometry"):
        resolve_placement(source, target, PlacementIntent(
            "s", "t", AnchorReference("center"), AnchorReference("outside"),
            coverage=CoverageIntent(0.25),
        ))
