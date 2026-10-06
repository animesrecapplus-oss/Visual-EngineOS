from __future__ import annotations

import pytest

from visual_engine.components.common.geometry_contract import GeometryContract, GeometryPrimitive
from visual_engine.runtime.consequences import (
    ConsequenceKind,
    ConsequenceRule,
    resolve_attribution_consequences,
)
from visual_engine.runtime.coverage import Occluder
from visual_engine.runtime.semantic_regions import RegionMap, rectangle_region
from visual_engine.runtime.visibility_attribution import resolve_visibility_attribution


def rect(x0: float, y0: float, x1: float, y1: float) -> GeometryContract:
    return GeometryContract(
        primitives=(
            GeometryPrimitive("polygon", {"points": ((x0, y0), (x1, y0), (x1, y1), (x0, y1))}),
        )
    )


def target() -> RegionMap:
    return RegionMap("target", (rectangle_region("surface", "surface", 0, 0, 10, 10),))


def test_compiler_uses_dominant_attribution_instead_of_pairwise_coverage():
    attribution = resolve_visibility_attribution(
        "target",
        target(),
        (
            Occluder("front", rect(0, 0, 7, 10), z=2),
            Occluder("back", rect(3, 0, 10, 10), z=1),
        ),
    )
    rule = ConsequenceRule(
        rule_id="dominant-majority",
        attribution_enabled=True,
        min_dominant_coverage=0.5,
        consequence_kind=ConsequenceKind.STATE,
        consequence_name="dominant-occlusion",
    )

    result = resolve_attribution_consequences(attribution, target(), [rule])

    assert [r.payload["occluder_id"] for r in result.requests] == ["front"]
    assert result.requests[0].payload["dominant_coverage"] == "0.7"


def test_pairwise_coverage_alone_does_not_trigger_dominant_rule():
    attribution = resolve_visibility_attribution(
        "target",
        target(),
        (
            Occluder("a", rect(0, 0, 7, 10), z=1),
            Occluder("b", rect(3, 0, 10, 10), z=2),
        ),
    )
    rule = ConsequenceRule(
        rule_id="dominant-majority",
        attribution_enabled=True,
        min_dominant_coverage=0.5,
        consequence_kind=ConsequenceKind.STATE,
        consequence_name="dominant-occlusion",
    )

    result = resolve_attribution_consequences(attribution, target(), [rule])

    assert [r.payload["occluder_id"] for r in result.requests] == ["b"]
    assert all(float(r.payload["coverage"]) >= 0.5 for r in result.requests)


def test_shared_and_exclusive_predicates_are_independent():
    attribution = resolve_visibility_attribution(
        "target",
        target(),
        (
            Occluder("a", rect(0, 0, 7, 10), z=2),
            Occluder("b", rect(3, 0, 10, 10), z=1),
        ),
    )
    shared_rule = ConsequenceRule(
        rule_id="shared",
        attribution_enabled=True,
        min_shared_coverage=0.4,
        max_shared_coverage=0.4,
        consequence_kind=ConsequenceKind.EFFECT,
        consequence_name="shared-layer",
    )
    exclusive_rule = ConsequenceRule(
        rule_id="exclusive",
        attribution_enabled=True,
        min_exclusive_coverage=0.3,
        max_exclusive_coverage=0.3,
        consequence_kind=ConsequenceKind.EFFECT,
        consequence_name="exclusive-layer",
    )

    result = resolve_attribution_consequences(attribution, target(), [shared_rule, exclusive_rule])

    assert len(result.requests) == 4
    assert {r.rule_id for r in result.requests} == {"shared", "exclusive"}


def test_optical_marginal_loss_is_not_reinterpreted_as_geometric_coverage():
    attribution = resolve_visibility_attribution(
        "target",
        target(),
        (
            Occluder("front", rect(0, 0, 7, 10), z=2),
            Occluder("back", rect(3, 0, 10, 10), z=1),
        ),
    )
    rule = ConsequenceRule(
        rule_id="causal-loss",
        attribution_enabled=True,
        min_optical_marginal_loss=0.31,
        consequence_kind=ConsequenceKind.APPEARANCE,
        consequence_name="causal-loss",
    )

    result = resolve_attribution_consequences(attribution, target(), [rule])

    # Each opaque layer has only 30% marginal loss in this arrangement.
    assert result.requests == ()


def test_attribution_target_must_match_region_map():
    attribution = resolve_visibility_attribution(
        "target",
        target(),
        (Occluder("a", rect(0, 0, 1, 1), z=1),),
    )
    with pytest.raises(ValueError, match="attribution target_id"):
        resolve_attribution_consequences(attribution, RegionMap("other", ()), [])


def test_existing_event_rule_does_not_fire_in_attribution_domain_without_opt_in():
    attribution = resolve_visibility_attribution(
        "target", target(), (Occluder("a", rect(0, 0, 10, 10), z=1),)
    )
    rule = ConsequenceRule(
        rule_id="legacy-event-rule",
        consequence_kind=ConsequenceKind.STATE,
        consequence_name="must-not-cross-domains",
    )

    result = resolve_attribution_consequences(attribution, target(), [rule])

    assert result.requests == ()
