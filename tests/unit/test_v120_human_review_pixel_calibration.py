from __future__ import annotations

import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from visual_engine.components.face.eyes import EyeParameters, build_eye_geometry
from visual_engine.components.face.eyes.reference import (
    CaruncleReview,
    EyeIdentification,
    EpicanthusReview,
    ReferenceCurve,
    ReferenceFamily,
    ReferenceSample,
    ReviewerStatus,
    TraceRegionV120,
    V120CandidateReview,
    aggregate_follow_strength_results,
    build_fixed_reference_engine_alignment,
    create_pending_v120_manifest,
    overlay_metrics,
    ReferenceEngineAlignment,
    evaluate_follow_strength_sample,
    load_v120_reviews,
    select_candidate_strength,
)


def _sample() -> ReferenceSample:
    upper = ReferenceCurve("upper", ((0.0, 0.0), (0.25, 0.10), (0.65, 0.16), (1.0, 0.0)))
    lower = ReferenceCurve("lower", ((0.0, 0.0), (0.25, -0.08), (0.65, -0.12), (1.0, 0.0)))
    return ReferenceSample(
        sample_id="S-A", family=ReferenceFamily.ANIME_STYLIZED,
        upper=upper, lower=lower, medial_terminal_px=(0.0, 0.0), lateral_terminal_px=(1.0, 0.0),
    )


def _approved() -> V120CandidateReview:
    return V120CandidateReview(
        candidate_id="candidate_001",
        source_bbox=TraceRegionV120(0, 0, 100, 100),
        eye_identification=EyeIdentification.YES,
        eye_side="single",
        upper_candidate_id="ink_001",
        lower_candidate_id="ink_002",
        medial_terminal_px=(10.0, 40.0),
        lateral_terminal_px=(90.0, 42.0),
        caruncle_status=CaruncleReview.UNKNOWN,
        epicanthus_status=EpicanthusReview.UNKNOWN,
        family=ReferenceFamily.UNCLASSIFIED,
        sample_id="S-001",
        reviewer_status=ReviewerStatus.APPROVED,
    )


def test_approved_review_requires_every_semantic_decision():
    with pytest.raises(ValueError, match="upper and lower"):
        V120CandidateReview(
            candidate_id="candidate_001", source_bbox=TraceRegionV120(0, 0, 10, 10),
            eye_identification=EyeIdentification.YES, eye_side="single", sample_id="S-001",
            reviewer_status=ReviewerStatus.APPROVED,
        )
    record = _approved()
    assert record.is_approved


def test_pending_manifest_covers_all_candidates_without_approval():
    segmentation = {
        "candidate_count": 2,
        "candidates": [
            {"candidate_id": "candidate_001", "bbox_px": {"x": 1, "y": 2, "width": 20, "height": 30}},
            {"candidate_id": "candidate_002", "bbox_px": {"x": 40, "y": 5, "width": 20, "height": 30}},
        ],
    }
    payload = create_pending_v120_manifest(segmentation, source_id="src", source_sha256="a" * 64)
    assert payload["candidate_count"] == 2
    assert payload["approved_count"] == 0
    assert all(row["reviewer_status"] == "pending_human_review" for row in payload["candidates"])



def test_outer_endpoint_tangent_uses_the_outer_terminal_not_the_inner_terminal():
    sample = _sample()
    engine = SimpleNamespace(
        upper_lid_points=sample.upper.points_px,
        lower_lid_points=sample.lower.points_px,
        inner_canthus=sample.medial_terminal_px,
        outer_canthus=sample.lateral_terminal_px,
    )
    alignment = ReferenceEngineAlignment(
        reference_medial_px=sample.medial_terminal_px,
        reference_lateral_px=sample.lateral_terminal_px,
        engine_medial=sample.medial_terminal_px,
        engine_lateral=sample.lateral_terminal_px,
        reference_normal_scale=0.28,
        engine_normal_scale=0.28,
    )
    metrics = overlay_metrics(sample, engine, alignment)
    assert metrics["inner_upper_tangent_error_deg"] == pytest.approx(0.0)
    assert metrics["outer_upper_tangent_error_deg"] == pytest.approx(0.0)
    assert metrics["inner_lower_tangent_error_deg"] == pytest.approx(0.0)
    assert metrics["outer_lower_tangent_error_deg"] == pytest.approx(0.0)

def test_real_pixel_alignment_does_not_modify_reference_geometry():
    sample = _sample()
    engine = build_eye_geometry(EyeParameters(width=1.0, height=0.3))
    alignment = build_fixed_reference_engine_alignment(sample, engine)
    assert alignment.reference_medial_px == sample.medial_terminal_px
    assert alignment.reference_lateral_px == sample.lateral_terminal_px
    assert alignment.reference_normal_scale > 0
    assert alignment.engine_normal_scale > 0


def test_follow_evaluation_requires_actual_common_strengths_and_is_deterministic():
    sample = _sample()

    def build(strength):
        return build_eye_geometry(EyeParameters(width=1.0, height=0.3, alignment_axis_rotation_deg=35.0,
                                                eyelid_surface_follow_strength=strength))

    result = evaluate_follow_strength_sample(sample, strengths=(0.0, 0.1, 0.2), build_engine=build)
    assert set(result["evaluations"]) == {"0.000000", "0.100000", "0.200000"}
    for row in result["evaluations"].values():
        assert row["scalar_errors"]["upper_error.rms_error"] >= 0
        assert row["scalar_errors"]["inner_upper_tangent_error_deg"] >= 0
        assert row["scalar_errors"]["outer_upper_tangent_error_deg"] >= 0


def test_aggregate_requires_two_independent_samples_and_selects_observed_value_only():
    rows = [
        {"sample_id": "a", "evaluations": {
            "0.000000": {"scalar_errors": {"upper_error.rms_error": 3.0}},
            "0.100000": {"scalar_errors": {"upper_error.rms_error": 1.0}},
        }},
        {"sample_id": "b", "evaluations": {
            "0.000000": {"scalar_errors": {"upper_error.rms_error": 2.0}},
            "0.100000": {"scalar_errors": {"upper_error.rms_error": 2.0}},
        }},
    ]
    aggregate = aggregate_follow_strength_results(rows)
    candidate = select_candidate_strength(aggregate)
    assert candidate["value"] == pytest.approx(0.1)
    assert candidate["status"] == "candidate_only"
    assert candidate["sample_count"] == 2


def test_aggregate_rejects_single_sample():
    with pytest.raises(ValueError, match="at least two"):
        aggregate_follow_strength_results([{"sample_id": "a", "evaluations": {}}])
