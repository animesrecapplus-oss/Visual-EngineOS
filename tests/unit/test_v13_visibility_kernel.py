from __future__ import annotations

from visual_engine.components.common.geometry_contract import GeometryContract, GeometryPrimitive
from visual_engine.runtime.coverage import DepthRelation, Occluder
from visual_engine.runtime.semantic_regions import RegionMap, rectangle_region, polygon_region
from visual_engine.runtime.visibility import (
    BooleanOperation, VisibilityEventKind, boolean_operation, difference_geometry,
    geometry_to_region, intersection_geometry, resolve_visibility, union_geometries,
)


def rect(x0, y0, x1, y1):
    return GeometryContract(primitives=(GeometryPrimitive("polygon", {"points": ((x0,y0),(x1,y0),(x1,y1),(x0,y1))}),))


def test_primitive_to_region_and_union_merge_overlapping_shapes_without_double_count():
    a = rect(0, 0, 10, 10)
    b = rect(5, 0, 15, 10)
    merged = union_geometries((a, b))
    assert abs(merged.area - 150.0) < 1e-8
    assert len(merged.polygons) == 1


def test_concave_polygon_intersection_is_not_limited_to_convex_clipping():
    target = polygon_region("target", "concave", ((0,0),(10,0),(10,4),(6,4),(6,10),(0,10)))
    occ = rect(4, 2, 8, 8)
    result = intersection_geometry(target.geometry, occ)
    assert 0 < result.area < target.geometry.bounds.max_x * target.geometry.bounds.max_y
    # The intersection contains the upper arm and lower bar, not a convex hull.
    assert len(result.polygons) >= 1


def test_difference_preserves_hole_topology():
    result = difference_geometry(rect(0,0,10,10), rect(3,3,7,7))
    assert abs(result.area - 84.0) < 1e-8
    assert len(result.polygons) == 1
    assert len(result.polygons[0].holes) == 1


def test_multi_occluder_overlap_is_counted_once():
    regions = RegionMap("target", (rectangle_region("surface", "surface", 0,0,10,10),))
    occluders = (
        Occluder("a", rect(0,0,7,10), z=2),
        Occluder("b", rect(3,0,10,10), z=1),
    )
    result = resolve_visibility("target", regions, occluders)
    r = result.regions[0]
    assert abs(r.coverage - 1.0) < 1e-8
    assert abs(result.overall_coverage - 1.0) < 1e-8


def test_multiple_occluders_without_full_overlap_have_correct_union_area():
    regions = RegionMap("target", (rectangle_region("surface", "surface", 0,0,10,10),))
    occluders = (
        Occluder("left", rect(0,0,3,10), z=2),
        Occluder("right", rect(7,0,10,10), z=1),
    )
    result = resolve_visibility("target", regions, occluders)
    assert abs(result.regions[0].coverage - 0.6) < 1e-8
    assert abs(result.regions[0].visible - 0.4) < 1e-8


def test_behind_occluders_do_not_enter_visibility_stack():
    regions = RegionMap("target", (rectangle_region("surface", "surface", 0,0,10,10),))
    result = resolve_visibility("target", regions, (Occluder("behind", rect(0,0,10,10), z=-1),))
    assert result.regions[0].coverage == 0
    assert result.regions[0].visible == 1
    assert result.events == ()


def test_transmission_is_optical_and_separate_from_geometric_coverage():
    regions = RegionMap("target", (rectangle_region("surface", "surface", 0,0,10,10),))
    result = resolve_visibility("target", regions, (Occluder("glass", rect(0,0,10,5), z=1, opacity=0.5, transmission=1.0),))
    r = result.regions[0]
    assert abs(r.coverage - 0.5) < 1e-8
    assert abs(r.visible - 1.0) < 1e-8
    assert r.transmitted_visibility > 0
    assert any(e.kind is VisibilityEventKind.TRANSMISSION for e in result.events)


def test_structured_events_identify_semantic_region_without_occluder_type():
    regions = RegionMap("eye", (rectangle_region("iris", "iris", 0,0,10,10),))
    result = resolve_visibility("eye", regions, (Occluder("arbitrary", rect(0,0,5,10), z=1),))
    assert {(e.region_id, e.occluder_id) for e in result.events} == {("iris", "arbitrary")}
    assert {e.kind for e in result.events} >= {VisibilityEventKind.COVERAGE, VisibilityEventKind.VISIBILITY, VisibilityEventKind.DEPTH}


def test_boolean_contract_is_deterministic():
    a, b = rect(0,0,8,8), rect(4,2,12,6)
    first = boolean_operation(a, b, BooleanOperation.INTERSECTION).geometry
    second = boolean_operation(a, b, BooleanOperation.INTERSECTION).geometry
    assert first == second
