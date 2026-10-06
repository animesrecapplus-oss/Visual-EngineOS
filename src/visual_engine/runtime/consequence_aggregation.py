from __future__ import annotations

"""Deterministic aggregation and conflict resolution for consequence requests.

This layer consumes declarative ``ConsequenceRequest`` objects and produces a
stable, immutable decision set. It does not mutate state, geometry, appearance,
or effects. Conflict semantics are explicit policy data; the resolver never
infers that two requests conflict merely because they target the same region.
"""

from dataclasses import dataclass
from enum import Enum
import hashlib
from typing import Iterable

from visual_engine.runtime.consequences import ConsequenceKind, ConsequenceRequest


class AggregationMode(str, Enum):
    KEEP_ALL = "keep_all"
    DEDUPLICATE = "deduplicate"
    HIGHEST_PRIORITY = "highest_priority"
    REJECT_CONFLICT = "reject_conflict"


@dataclass(frozen=True, slots=True)
class ConsequencePolicy:
    """Declarative resolution policy for a logical consequence group."""

    group: str
    mode: AggregationMode = AggregationMode.DEDUPLICATE
    priority: int = 0

    def __post_init__(self) -> None:
        if not self.group:
            raise ValueError("policy group must not be empty")
        if not isinstance(self.priority, int):
            raise ValueError("policy priority must be an integer")


@dataclass(frozen=True, slots=True)
class ConsequenceProvenance:
    """Stable causal provenance retained without mutating the request payload."""

    rule_id: str
    target_id: str
    region_id: str
    source_event_key: tuple[str, str, str, str]


@dataclass(frozen=True, slots=True)
class ResolvedConsequence:
    request: ConsequenceRequest
    provenance: ConsequenceProvenance
    fingerprint: str
    policy_group: str
    decision: str
    rejected_request_fingerprints: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ConsequenceAggregationResult:
    target_id: str
    resolved: tuple[ResolvedConsequence, ...]
    rejected: tuple[ResolvedConsequence, ...]
    digest: str

    @property
    def requests(self) -> tuple[ConsequenceRequest, ...]:
        return tuple(item.request for item in self.resolved)


def request_fingerprint(request: ConsequenceRequest) -> str:
    """Hash the semantic request, excluding no causal fields by accident."""
    payload = "\n".join(f"{k}={v}" for k, v in sorted(request.payload.items()))
    canonical = "|".join((
        request.rule_id,
        request.kind.value,
        request.target_id,
        request.region_id,
        *request.source_event_key,
        str(request.precedence),
        payload,
    ))
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _logical_key(request: ConsequenceRequest, group: str) -> tuple[str, str, ConsequenceKind, str, str]:
    return (request.target_id, request.region_id, request.kind, group, request.payload.get("consequence", ""))


def _ordered(items: Iterable[ConsequenceRequest]) -> list[ConsequenceRequest]:
    return sorted(items, key=lambda r: (
        r.target_id, r.region_id, r.kind.value, r.rule_id,
        r.source_event_key, tuple(sorted(r.payload.items())),
    ))


def aggregate_consequence_requests(
    requests: tuple[ConsequenceRequest, ...] | list[ConsequenceRequest],
    policies: tuple[ConsequencePolicy, ...] | list[ConsequencePolicy] = (),
) -> ConsequenceAggregationResult:
    """Aggregate requests deterministically, fail-closed on ambiguous policies.

    A request is deduplicated by its complete semantic fingerprint. Conflict
    grouping is only activated when a policy explicitly names a group through
    the request's ``payload['resolution_group']`` value; absent that declaration,
    requests remain independent. This prevents accidental suppression of
    legitimate effects that merely share a target region.
    """
    policy_map: dict[str, ConsequencePolicy] = {}
    for policy in policies:
        if policy.group in policy_map:
            raise ValueError(f"duplicate consequence policy group: {policy.group}")
        policy_map[policy.group] = policy

    ordered = _ordered(requests)
    seen: dict[str, ResolvedConsequence] = {}
    candidates: dict[tuple[str, str, ConsequenceKind, str, str], list[ResolvedConsequence]] = {}

    for request in ordered:
        fingerprint = request_fingerprint(request)
        if fingerprint in seen:
            continue
        group = request.payload.get("resolution_group", "")
        policy = policy_map.get(group) if group else None
        provenance = ConsequenceProvenance(request.rule_id, request.target_id, request.region_id, request.source_event_key)
        item = ResolvedConsequence(request, provenance, fingerprint, group, "accepted")
        seen[fingerprint] = item
        if policy is None or policy.mode is AggregationMode.KEEP_ALL:
            candidates.setdefault((request.target_id, request.region_id, request.kind, group, request.payload.get("consequence", "")), []).append(item)
        else:
            candidates.setdefault(_logical_key(request, group), []).append(item)

    accepted: list[ResolvedConsequence] = []
    rejected: list[ResolvedConsequence] = []
    for key in sorted(candidates, key=lambda k: (k[0], k[1], k[2].value, k[3], k[4])):
        group = key[3]
        policy = policy_map.get(group) if group else None
        bucket = candidates[key]
        if policy is None or policy.mode in {AggregationMode.KEEP_ALL, AggregationMode.DEDUPLICATE}:
            accepted.extend(bucket)
            continue
        if policy.mode is AggregationMode.HIGHEST_PRIORITY:
            # Priority belongs to the explicit policy group, not ConsequenceRule.priority.
            # Ties are resolved by complete request fingerprint, making the result stable.
            winner = max(bucket, key=lambda item: (item.request.precedence, item.fingerprint))
            accepted.append(winner)
            for item in bucket:
                if item is not winner:
                    rejected.append(ResolvedConsequence(
                        item.request, item.provenance, item.fingerprint, group, "rejected_precedence",
                        tuple(x.fingerprint for x in bucket if x is not winner),
                    ))
            continue
        if policy.mode is AggregationMode.REJECT_CONFLICT:
            if len(bucket) > 1:
                for item in bucket:
                    rejected.append(ResolvedConsequence(
                        item.request, item.provenance, item.fingerprint, group, "rejected_conflict",
                        tuple(x.fingerprint for x in bucket if x is not item),
                    ))
            else:
                accepted.extend(bucket)
            continue
        raise ValueError(f"unsupported aggregation mode: {policy.mode}")

    accepted.sort(key=lambda x: (x.request.target_id, x.request.region_id, x.request.kind.value, x.request.rule_id, x.fingerprint))
    rejected.sort(key=lambda x: (x.request.target_id, x.request.region_id, x.request.kind.value, x.request.rule_id, x.fingerprint))
    digest_input = "\n".join(x.fingerprint + ":" + x.decision for x in (*accepted, *rejected))
    digest = hashlib.sha256(digest_input.encode("ascii")).hexdigest()
    target_ids = {x.request.target_id for x in (*accepted, *rejected)}
    if len(target_ids) > 1:
        raise ValueError("consequence aggregation must operate on one target_id")
    target_id = next(iter(target_ids), "")
    return ConsequenceAggregationResult(target_id, tuple(accepted), tuple(rejected), digest)
