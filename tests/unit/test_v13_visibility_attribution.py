from __future__ import annotations

import pytest

from visual_engine.components.common.geometry_contract import GeometryContract, GeometryPrimitive
from visual_engine.runtime.coverage import DepthRelation, Occluder
from visual_engine.runtime.semantic_regions import RegionMap, rectangle_region
from visual_engine.runtime.visibility_attribution import resolve_visibility_attribution


def rect(x0, y0, x1, y1):
    return GeometryContract(
        primitives=(GeometryPrimitive("polygon", {"points": ((x0, y0), (x1, y0), (x1, y1), (x0, y1))}),)
    )


def target():
    return RegionMap("target", (rectangle_region("surface", "surface", 0, 0, 10, 10),))


def by_id(result, oid):
    return next(a for a in result.attributions if a.occluder_id == oid)


def test_disjoint_occluders_have_exclusive_and_dominant_coverage_without_double_counting():
    result = resolve_visibility_attribution(
        "target", target(),
        (Occluder("left", rect(0, 0, 3, 10), z=2), Occluder("right", rect(7, 0, 10, 10), z=1)),
    )
    left, right = by_id(result, "left"), by_id(result, "right")
    assert left.coverage == pytest.approx(0.3)
    assert right.coverage == pytest.approx(0.3)
    assert left.exclusive_coverage == pytest.approx(0.3)
    assert right.exclusive_coverage == pytest.approx(0.3)
    assert left.shared_coverage == pytest.approx(0.0)
    assert right.shared_coverage == pytest.approx(0.0)
    assert left.dominant_coverage == pytest.approx(0.3)
    assert right.dominant_coverage == pytest.approx(0.3)


def test_overlapping_occluders_are_partitioned_into_exclusive_shared_and_dominant_area():
    result = resolve_visibility_attribution(
        "target", target(),
        (Occluder("a", rect(0, 0, 7, 10), z=2), Occluder("b", rect(3, 0, 10, 10), z=1)),
    )
    a, b = by_id(result, "a"), by_id(result, "b")
    # A covers 70%, B covers 70%; the central 40% is shared.
    assert a.coverage == pytest.approx(0.7)
    assert b.coverage == pytest.approx(0.7)
    assert a.exclusive_coverage == pytest.approx(0.3)
    assert b.exclusive_coverage == pytest.approx(0.3)
    assert a.shared_coverage == pytest.approx(0.4)
    assert b.shared_coverage == pytest.approx(0.4)
    # A is in front, therefore it dominates the overlap plus its exclusive part.
    assert a.dominant_coverage == pytest.approx(0.7)
    assert b.dominant_coverage == pytest.approx(0.3)


def test_reversing_depth_reverses_dominant_attribution_but_not_geometric_coverage():
    result = resolve_visibility_attribution(
        "target", target(),
        (Occluder("a", rect(0, 0, 7, 10), z=1), Occluder("b", rect(3, 0, 10, 10), z=2)),
    )
    a, b = by_id(result, "a"), by_id(result, "b")
    assert a.coverage == pytest.approx(0.7)
    assert b.coverage == pytest.approx(0.7)
    assert a.dominant_coverage == pytest.approx(0.3)
    assert b.dominant_coverage == pytest.approx(0.7)


def test_marginal_optical_loss_is_zero_for_fully_transmissive_layer():
    result = resolve_visibility_attribution(
        "target", target(),
        (Occluder("glass", rect(0, 0, 10, 5), z=1, opacity=1.0, transmission=1.0),),
    )
    assert by_id(result, "glass").optical_marginal_loss == pytest.approx(0.0)


def test_marginal_optical_loss_is_exact_counterfactual_for_two_opaque_overlapping_layers():
    result = resolve_visibility_attribution(
        "target", target(),
        (Occluder("front", rect(0, 0, 7, 10), z=2), Occluder("back", rect(3, 0, 10, 10), z=1)),
    )
    front, back = by_id(result, "front"), by_id(result, "back")
    # Removing either layer reveals exactly its exclusive footprint: the front
    # layer owns the 30% left-exclusive area after the back is restored, while
    # the back layer owns the 30% right-exclusive area. The 40% overlap remains
    # covered by the other opaque layer in either counterfactual.
    assert front.optical_marginal_loss == pytest.approx(0.3)
    assert back.optical_marginal_loss == pytest.approx(0.3)


def test_attribution_is_invariant_to_occluder_input_order():
    a = Occluder("a", rect(0, 0, 7, 10), z=2)
    b = Occluder("b", rect(3, 0, 10, 10), z=1)
    first = resolve_visibility_attribution("target", target(), (a, b))
    second = resolve_visibility_attribution("target", target(), (b, a))
    assert first == second


def test_duplicate_occluder_ids_are_rejected():
    a = Occluder("same", rect(0, 0, 5, 10), z=2)
    b = Occluder("same", rect(5, 0, 10, 10), z=1)
    with pytest.raises(ValueError, match="occluder IDs must be unique"):
        resolve_visibility_attribution("target", target(), (a, b))


def test_behind_occluders_are_not_attributed():
    result = resolve_visibility_attribution(
        "target", target(), (Occluder("behind", rect(0, 0, 10, 10), z=-1),)
    )
    assert result.attributions == ()


def test_dominant_coverage_is_never_greater_than_pairwise_coverage():
    result = resolve_visibility_attribution(
        "target", target(),
        (
            Occluder("a", rect(0, 0, 8, 10), z=3),
            Occluder("b", rect(2, 0, 10, 10), z=2),
            Occluder("c", rect(4, 0, 6, 10), z=1),
        ),
    )
    for attribution in result.attributions:
        assert attribution.dominant_coverage <= attribution.coverage + 1e-9
        assert attribution.exclusive_coverage + attribution.shared_coverage == pytest.approx(attribution.coverage)
