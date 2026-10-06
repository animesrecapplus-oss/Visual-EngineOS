from __future__ import annotations

import pytest

from visual_engine.runtime.consequence_aggregation import (
    AggregationMode,
    ConsequencePolicy,
    aggregate_consequence_requests,
    request_fingerprint,
)
from visual_engine.runtime.consequences import ConsequenceKind, ConsequenceRequest


def req(rule="r", region="face", event="e", consequence="mark", precedence=0, **payload):
    p = {"consequence": consequence, **payload}
    return ConsequenceRequest(rule, ConsequenceKind.STATE, "target", region, ("target", region, event, "visibility"), p, precedence)


def test_exact_duplicates_are_idempotently_removed():
    a = req()
    result = aggregate_consequence_requests([a, a])
    assert len(result.requests) == 1
    assert not result.rejected


def test_same_target_different_causes_remain_independent_without_policy():
    result = aggregate_consequence_requests([req(event="e1"), req(event="e2")])
    assert len(result.requests) == 2


def test_explicit_conflict_group_rejects_competing_requests():
    a = req(rule="a", event="e1", resolution_group="eye_state")
    b = req(rule="b", event="e2", resolution_group="eye_state")
    result = aggregate_consequence_requests([a, b], [ConsequencePolicy("eye_state", AggregationMode.REJECT_CONFLICT)])
    assert not result.requests
    assert len(result.rejected) == 2
    assert all(x.decision == "rejected_conflict" for x in result.rejected)


def test_keep_all_policy_preserves_distinct_requests_in_same_group():
    a = req(event="e1", resolution_group="effects")
    b = req(event="e2", resolution_group="effects")
    result = aggregate_consequence_requests([a, b], [ConsequencePolicy("effects", AggregationMode.KEEP_ALL)])
    assert len(result.requests) == 2


def test_precedence_is_explicit_and_deterministic():
    a = req(rule="a", event="e1", resolution_group="state", precedence=10)
    b = req(rule="b", event="e2", resolution_group="state", precedence=20)
    result = aggregate_consequence_requests([a, b], [ConsequencePolicy("state", AggregationMode.HIGHEST_PRIORITY)])
    assert [x.request.rule_id for x in result.resolved] == ["b"]
    assert result.rejected[0].decision == "rejected_precedence"


def test_provenance_and_digest_are_stable():
    a = req()
    first = aggregate_consequence_requests([a])
    second = aggregate_consequence_requests([a])
    assert first.digest == second.digest
    assert first.resolved[0].provenance.source_event_key == a.source_event_key
    assert first.resolved[0].fingerprint == request_fingerprint(a)


def test_multiple_targets_fail_closed():
    a = req()
    b = ConsequenceRequest("b", ConsequenceKind.STATE, "other", "face", ("other", "face", "e", "visibility"), {"consequence": "mark"})
    with pytest.raises(ValueError, match="one target_id"):
        aggregate_consequence_requests([a, b])


def test_unknown_policy_mode_cannot_be_silently_accepted():
    with pytest.raises(ValueError, match="policy group"):
        ConsequencePolicy("")
