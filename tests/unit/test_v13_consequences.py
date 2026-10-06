from __future__ import annotations

from visual_engine.components.common.geometry_contract import GeometryContract, GeometryPrimitive
from visual_engine.runtime.consequences import ConsequenceKind, ConsequenceRule, resolve_consequences
from visual_engine.runtime.coverage import Occluder
from visual_engine.runtime.semantic_regions import RegionKind, RegionMap, rectangle_region
from visual_engine.runtime.visibility import VisibilityEventKind, resolve_visibility


def rect(x0, y0, x1, y1):
    return GeometryContract(primitives=(GeometryPrimitive("polygon", {"points": ((x0,y0),(x1,y0),(x1,y1),(x0,y1))}),))


def test_consequence_rule_matches_region_semantics_not_occluder_type():
    regions = RegionMap("target", (rectangle_region("r", "arbitrary-region", 0, 0, 10, 10, kind=RegionKind.SUBREGION, tags=("sensitive",)),))
    visibility = resolve_visibility("target", regions, (Occluder("any-object", rect(0, 0, 5, 10), z=1),))
    rule = ConsequenceRule(
        "partial-sensitive", event_kind=VisibilityEventKind.COVERAGE,
        region_kinds=("subregion",), region_tags=("sensitive",),
        min_coverage=0.4, max_coverage=0.6,
        consequence_kind=ConsequenceKind.STATE, consequence_name="covered-partially",
    )
    result = resolve_consequences(visibility.events, regions, (rule,))
    assert result.matched_rule_ids == ("partial-sensitive",)
    assert result.requests[0].region_id == "r"
    assert result.requests[0].payload["occluder_id"] == "any-object"


def test_consequence_thresholds_are_deterministic_and_do_not_mutate_event():
    regions = RegionMap("target", (rectangle_region("r", "region", 0, 0, 10, 10),))
    visibility = resolve_visibility("target", regions, (Occluder("o", rect(0, 0, 2, 10), z=1),))
    rule = ConsequenceRule(
        "too-much", event_kind=VisibilityEventKind.COVERAGE,
        min_coverage=0.3, consequence_kind=ConsequenceKind.GEOMETRY,
        consequence_name="deform",
    )
    result = resolve_consequences(visibility.events, regions, (rule,))
    assert result.requests == ()
    assert visibility.regions[0].coverage == 0.2


def test_multiple_rules_are_priority_ordered_but_requests_are_canonically_sorted():
    regions = RegionMap("target", (rectangle_region("r", "region", 0, 0, 10, 10),))
    visibility = resolve_visibility("target", regions, (Occluder("o", rect(0, 0, 5, 10), z=1),))
    rules = (
        ConsequenceRule("b", event_kind=VisibilityEventKind.COVERAGE, consequence_kind=ConsequenceKind.EFFECT, consequence_name="b", priority=0),
        ConsequenceRule("a", event_kind=VisibilityEventKind.COVERAGE, consequence_kind=ConsequenceKind.STATE, consequence_name="a", priority=10),
    )
    result = resolve_consequences(visibility.events, regions, rules)
    assert [r.rule_id for r in result.requests] == ["a", "b"]
    assert result.matched_rule_ids == ("a", "b")
