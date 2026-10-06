from __future__ import annotations

import hashlib
from pathlib import Path
from types import SimpleNamespace

import pytest

from visual_engine.components.face.eyes.reference.digitization import ReferenceCurve, ReferenceFamily, ReferenceSample
from visual_engine.components.face.eyes.reference.v120_review import V120CandidateReview
from visual_engine.components.face.eyes.reference.v121_trace_capture import TraceRegionV121, V121TraceCapture
from visual_engine.components.face.eyes.reference.v122_sample_gate import V122DigitizedSample, build_dual_sample_gate, qualify_sample
from visual_engine.components.face.eyes.reference.review import ReviewerStatus

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "references/v1.10/sources/user_supplied/reference_sheet_2026-09-18.jpg"


def pending_review(candidate_id: str) -> V120CandidateReview:
    return V120CandidateReview(candidate_id, SimpleNamespace(x=0, y=0, width=20, height=20))


def capture(candidate_id: str) -> V121TraceCapture:
    return V121TraceCapture(candidate_id, TraceRegionV121(0, 0, 20, 20), "component", "component", "ink_001", "ink_002")


def sample(sample_id: str) -> ReferenceSample:
    upper = ReferenceCurve("upper", ((0, 0), (2, 1), (4, 0), (6, -1)))
    lower = ReferenceCurve("lower", ((0, 3), (2, 4), (4, 3), (6, 2)))
    return ReferenceSample(sample_id, ReferenceFamily.UNCLASSIFIED, upper, lower, (0, 0), (6, 0))


def approved_review(candidate_id: str, sample_id: str) -> V120CandidateReview:
    return V120CandidateReview(
        candidate_id, SimpleNamespace(x=0, y=0, width=20, height=20),
        eye_identification="yes", eye_side="single", upper_candidate_id="ink_001", lower_candidate_id="ink_002",
        medial_terminal_px=(0, 0), lateral_terminal_px=(6, 0), sample_id=sample_id,
        reviewer_status=ReviewerStatus.APPROVED,
    )


def digitized(candidate_id: str, sample_id: str) -> V122DigitizedSample:
    return V122DigitizedSample(candidate_id, sample(sample_id), hashlib.sha256(SOURCE.read_bytes()).hexdigest(), (792, 792), "component")


def test_zero_approval_gate_is_closed():
    gate = build_dual_sample_gate(SOURCE, [pending_review("candidate_001")], [capture("candidate_001")], [])
    assert gate.status == "BLOCKED_PENDING_TWO_INDEPENDENT_APPROVED_SAMPLES"
    assert not gate.eligible
    assert gate.audit()["qualified_count"] == 0


def test_one_approved_sample_is_still_closed():
    review = approved_review("candidate_001", "sample_a")
    gate = build_dual_sample_gate(SOURCE, [review], [capture("candidate_001")], [digitized("candidate_001", "sample_a")])
    assert not gate.eligible
    assert gate.audit()["qualified_count"] == 1


def test_two_independent_approved_samples_open_gate():
    reviews = [approved_review("candidate_001", "sample_a"), approved_review("candidate_002", "sample_b")]
    captures = [capture("candidate_001"), capture("candidate_002")]
    digitized_samples = [digitized("candidate_001", "sample_a"), digitized("candidate_002", "sample_b")]
    gate = build_dual_sample_gate(SOURCE, reviews, captures, digitized_samples)
    assert gate.eligible
    assert gate.status == "READY_FOR_REAL_PIXEL_CALIBRATION"


def test_duplicate_sample_ids_fail_at_review_boundary():
    with pytest.raises(ValueError):
        approved_review("candidate_002", "sample_a")
        # The manifest loader, not the record constructor, owns cross-record uniqueness.
        build_dual_sample_gate(SOURCE,
            [approved_review("candidate_001", "sample_a"), approved_review("candidate_002", "sample_a")],
            [capture("candidate_001"), capture("candidate_002")], [digitized("candidate_001", "sample_a"), digitized("candidate_002", "sample_a")])


def test_missing_capture_is_explicit_blocker():
    review = approved_review("candidate_001", "sample_a")
    gate = build_dual_sample_gate(SOURCE, [review], [], [digitized("candidate_001", "sample_a")])
    assert gate.qualifications[0].blockers == ("trace_capture_missing",)


def test_source_fingerprint_is_real():
    review = pending_review("candidate_001")
    q = qualify_sample(SOURCE, review, capture("candidate_001"), None)
    assert q.source_sha256 == hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    assert q.source_dimensions == (792, 792)


def test_real_digitization_cannot_bypass_human_gate():
    from visual_engine.components.face.eyes.reference.v122_sample_gate import digitize_v122_sample
    with pytest.raises(ValueError, match="explicitly approved"):
        digitize_v122_sample(SOURCE, pending_review("candidate_001"), capture("candidate_001"))


def test_tampered_source_provenance_blocks_qualification():
    review = approved_review("candidate_001", "sample_a")
    d = V122DigitizedSample("candidate_001", sample("sample_a"), "0" * 64, (792, 792), "component")
    q = qualify_sample(SOURCE, review, capture("candidate_001"), d)
    assert "source_fingerprint_mismatch" in q.blockers
    assert not q.eligible_for_calibration
