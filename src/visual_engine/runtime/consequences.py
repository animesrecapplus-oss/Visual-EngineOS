from __future__ import annotations

"""Generic consequence resolution for semantic visibility events.

This module deliberately does not know anatomy or object categories. Rules match
properties of a visibility event and a semantic region, then emit declarative
requests. They do not mutate geometry/state themselves; downstream resolvers
remain responsible for applying the requests.
"""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Mapping

from visual_engine.runtime.semantic_regions import RegionMap
from visual_engine.runtime.visibility import AffectedRegionEvent, VisibilityEventKind
from visual_engine.runtime.visibility_attribution import OccluderAttribution, VisibilityAttributionResult


class ConsequenceKind(str, Enum):
    STATE = "state"
    EFFECT = "effect"
    GEOMETRY = "geometry"
    APPEARANCE = "appearance"


@dataclass(frozen=True, slots=True)
class ConsequenceRequest:
    rule_id: str
    kind: ConsequenceKind
    target_id: str
    region_id: str
    source_event_key: tuple[str, str, str, str]
    payload: Mapping[str, str] = field(default_factory=dict)
    # Downstream aggregation precedence is intentionally separate from rule priority.
    precedence: int = 0

    def __post_init__(self) -> None:
        if not self.rule_id or not self.target_id or not self.region_id:
            raise ValueError("consequence identifiers are required")
        if not isinstance(self.precedence, int):
            raise ValueError("consequence precedence must be an integer")
        object.__setattr__(self, "payload", dict(sorted(self.payload.items())))


@dataclass(frozen=True, slots=True)
class ConsequenceRule:
    """Data-only event predicate plus a declarative downstream request."""

    rule_id: str
    event_kind: VisibilityEventKind | None = None
    region_kinds: tuple[str, ...] = ()
    region_tags: tuple[str, ...] = ()
    min_coverage: float = 0.0
    max_coverage: float = 1.0
    min_visible: float = 0.0
    max_visible: float = 1.0
    min_transmitted_visibility: float = 0.0
    max_transmitted_visibility: float = 1.0
    # Attribution predicates are optional and are evaluated only by the
    # attribution-specific resolver. They never reinterpret ordinary
    # AffectedRegionEvent.coverage/visible fields.
    attribution_enabled: bool = False
    min_exclusive_coverage: float = 0.0
    max_exclusive_coverage: float = 1.0
    min_shared_coverage: float = 0.0
    max_shared_coverage: float = 1.0
    min_dominant_coverage: float = 0.0
    max_dominant_coverage: float = 1.0
    min_optical_marginal_loss: float = 0.0
    max_optical_marginal_loss: float = 1.0
    depth_relations: tuple[str, ...] = ()
    consequence_kind: ConsequenceKind = ConsequenceKind.STATE
    consequence_name: str = ""
    payload: Mapping[str, str] = field(default_factory=dict)
    priority: int = 0

    def __post_init__(self) -> None:
        if not self.rule_id:
            raise ValueError("rule_id must not be empty")
        for name, low, high in (
            ("coverage", self.min_coverage, self.max_coverage),
            ("visible", self.min_visible, self.max_visible),
            ("transmitted_visibility", self.min_transmitted_visibility, self.max_transmitted_visibility),
            ("exclusive_coverage", self.min_exclusive_coverage, self.max_exclusive_coverage),
            ("shared_coverage", self.min_shared_coverage, self.max_shared_coverage),
            ("dominant_coverage", self.min_dominant_coverage, self.max_dominant_coverage),
            ("optical_marginal_loss", self.min_optical_marginal_loss, self.max_optical_marginal_loss),
        ):
            for field_name, value in ((f"min_{name}", low), (f"max_{name}", high)):
                if not math.isfinite(value) or not 0 <= value <= 1:
                    raise ValueError(f"{field_name} must be in [0,1]")
            if low > high:
                raise ValueError(f"min_{name} must be <= max_{name}")
        if not self.consequence_name:
            raise ValueError("consequence_name must not be empty")
        if not isinstance(self.priority, int):
            raise ValueError("priority must be an integer")
        object.__setattr__(self, "region_kinds", tuple(sorted(set(self.region_kinds))))
        object.__setattr__(self, "region_tags", tuple(sorted(set(self.region_tags))))
        object.__setattr__(self, "depth_relations", tuple(sorted(set(self.depth_relations))))
        object.__setattr__(self, "payload", dict(sorted(self.payload.items())))

    def matches(self, event: AffectedRegionEvent, regions: RegionMap) -> bool:
        if self.event_kind is not None and event.kind is not self.event_kind:
            return False
        if not self.min_coverage <= event.coverage <= self.max_coverage:
            return False
        if not self.min_visible <= event.visible <= self.max_visible:
            return False
        if not self.min_transmitted_visibility <= event.transmitted_visibility <= self.max_transmitted_visibility:
            return False
        if self.depth_relations and event.depth_relation.value not in self.depth_relations:
            return False
        region = regions.get(event.region_id)
        if self.region_kinds and region.kind.value not in self.region_kinds:
            return False
        if self.region_tags and not set(self.region_tags).issubset(region.tags):
            return False
        return True

    def matches_attribution(self, attribution: OccluderAttribution, regions: RegionMap) -> bool:
        """Match causal-attribution measurements without changing event semantics.

        Attribution rules require explicit opt-in. This prevents an existing
        event rule, whose default ranges are intentionally broad, from silently
        firing on a different event domain.
        """
        if not self.attribution_enabled:
            return False
        if not self.min_coverage <= attribution.coverage <= self.max_coverage:
            return False
        if not self.min_exclusive_coverage <= attribution.exclusive_coverage <= self.max_exclusive_coverage:
            return False
        if not self.min_shared_coverage <= attribution.shared_coverage <= self.max_shared_coverage:
            return False
        if not self.min_dominant_coverage <= attribution.dominant_coverage <= self.max_dominant_coverage:
            return False
        if not self.min_optical_marginal_loss <= attribution.optical_marginal_loss <= self.max_optical_marginal_loss:
            return False
        if self.depth_relations and attribution.depth_relation.value not in self.depth_relations:
            return False
        region = regions.get(attribution.region_id)
        if self.region_kinds and region.kind.value not in self.region_kinds:
            return False
        if self.region_tags and not set(self.region_tags).issubset(region.tags):
            return False
        return True


@dataclass(frozen=True, slots=True)
class ConsequenceResolution:
    target_id: str
    requests: tuple[ConsequenceRequest, ...]
    matched_rule_ids: tuple[str, ...]


def resolve_consequences(
    events: tuple[AffectedRegionEvent, ...] | list[AffectedRegionEvent],
    regions: RegionMap,
    rules: tuple[ConsequenceRule, ...] | list[ConsequenceRule],
) -> ConsequenceResolution:
    """Evaluate rules deterministically without applying their consequences."""
    ordered_events = tuple(sorted(events, key=lambda e: (e.region_id, e.occluder_id, e.kind.value)))
    ordered_rules = tuple(sorted(rules, key=lambda r: (-r.priority, r.rule_id)))
    requests: list[ConsequenceRequest] = []
    matched: set[str] = set()
    for event in ordered_events:
        for rule in ordered_rules:
            if not rule.matches(event, regions):
                continue
            matched.add(rule.rule_id)
            payload = dict(rule.payload)
            payload.update({
                "consequence": rule.consequence_name,
                "coverage": f"{event.coverage:.12g}",
                "visible": f"{event.visible:.12g}",
                "transmitted_visibility": f"{event.transmitted_visibility:.12g}",
                "depth_relation": event.depth_relation.value,
                "occluder_id": event.occluder_id,
            })
            requests.append(ConsequenceRequest(
                rule.rule_id,
                rule.consequence_kind,
                event.target_id,
                event.region_id,
                (event.target_id, event.region_id, event.occluder_id, event.kind.value),
                payload,
            ))
    requests.sort(key=lambda r: (r.target_id, r.region_id, r.source_event_key, r.rule_id, r.kind.value))
    return ConsequenceResolution(regions.target_id, tuple(requests), tuple(sorted(matched)))


def resolve_attribution_consequences(
    attribution: VisibilityAttributionResult,
    regions: RegionMap,
    rules: tuple[ConsequenceRule, ...] | list[ConsequenceRule],
) -> ConsequenceResolution:
    """Compile causal attribution into declarative consequence requests.

    This resolver consumes only already-resolved attribution facts. It never
    applies state, geometry, appearance, or effect mutations. Ordinary
    ``resolve_consequences`` remains unchanged and continues to consume
    ``AffectedRegionEvent`` objects.
    """
    if attribution.target_id != regions.target_id:
        raise ValueError("attribution target_id must match RegionMap target_id")

    ordered = tuple(sorted(attribution.attributions, key=lambda a: (a.region_id, a.occluder_id)))
    ordered_rules = tuple(sorted(rules, key=lambda r: (-r.priority, r.rule_id)))
    requests: list[ConsequenceRequest] = []
    matched: set[str] = set()
    for item in ordered:
        for rule in ordered_rules:
            if not rule.matches_attribution(item, regions):
                continue
            matched.add(rule.rule_id)
            payload = dict(rule.payload)
            payload.update({
                "consequence": rule.consequence_name,
                "coverage": f"{item.coverage:.12g}",
                "exclusive_coverage": f"{item.exclusive_coverage:.12g}",
                "shared_coverage": f"{item.shared_coverage:.12g}",
                "dominant_coverage": f"{item.dominant_coverage:.12g}",
                "optical_marginal_loss": f"{item.optical_marginal_loss:.12g}",
                "depth_relation": item.depth_relation.value,
                "occluder_id": item.occluder_id,
            })
            requests.append(ConsequenceRequest(
                rule.rule_id,
                rule.consequence_kind,
                item.target_id,
                item.region_id,
                (item.target_id, item.region_id, item.occluder_id, "causal_attribution"),
                payload,
            ))
    requests.sort(key=lambda r: (r.target_id, r.region_id, r.source_event_key, r.rule_id, r.kind.value))
    return ConsequenceResolution(attribution.target_id, tuple(requests), tuple(sorted(matched)))
