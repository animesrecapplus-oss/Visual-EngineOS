from __future__ import annotations

import pytest

from visual_engine.components.face.eyes.reference import (
    CaruncleReview, EyeIdentification, EpicanthusReview, ManualPolylineV121,
    ReferenceFamily, ReviewerStatus, TraceRegionV120, TraceRegionV121,
    V120CandidateReview, V121TraceCapture, digitize_v121_capture,
    MANUAL_UPPER_TRACE_ID, MANUAL_LOWER_TRACE_ID,
    load_trace_capture, trace_capture_to_json,
)


def _approved() -> V120CandidateReview:
    return V120CandidateReview(
        candidate_id="candidate_014", source_bbox=TraceRegionV120(665, 274, 104, 105),
        eye_identification=EyeIdentification.YES, eye_side="single",
        upper_candidate_id=MANUAL_UPPER_TRACE_ID, lower_candidate_id=MANUAL_LOWER_TRACE_ID,
        medial_terminal_px=(680.0, 325.0), lateral_terminal_px=(745.0, 330.0),
        caruncle_status=CaruncleReview.UNKNOWN, epicanthus_status=EpicanthusReview.UNKNOWN,
        family=ReferenceFamily.UNCLASSIFIED, sample_id="S-014", reviewer_status=ReviewerStatus.APPROVED,
    )


def _manual_capture() -> V121TraceCapture:
    upper = ManualPolylineV121(((680, 325), (695, 312), (715, 305), (735, 312), (745, 330)))
    lower = ManualPolylineV121(((680, 325), (695, 338), (715, 341), (735, 338), (745, 330)))
    return V121TraceCapture(
        candidate_id="candidate_014", trace_region=TraceRegionV121(670, 295, 85, 55),
        upper_mode="manual", lower_mode="manual", upper_manual=upper, lower_manual=lower,
    )


def test_manual_trace_supports_connected_components_without_semantic_auto_split():
    sample = digitize_v121_capture("unused.jpg", _approved(), _manual_capture())
    assert len(sample.upper.points_px) == 5
    assert len(sample.lower.points_px) == 5
    assert sample.medial_terminal_px == (680.0, 325.0)
    assert "no curve fit substituted" in sample.notes


def test_manual_trace_is_oriented_from_medial_terminal():
    cap = _manual_capture()
    reversed_upper = ManualPolylineV121(tuple(reversed(cap.upper_manual.points_px)))
    reversed_lower = ManualPolylineV121(tuple(reversed(cap.lower_manual.points_px)))
    cap = V121TraceCapture(
        candidate_id=cap.candidate_id, trace_region=cap.trace_region,
        upper_mode="manual", lower_mode="manual", upper_manual=reversed_upper, lower_manual=reversed_lower,
    )
    sample = digitize_v121_capture("unused.jpg", _approved(), cap)
    assert sample.upper.points_px[0] == (680, 325)
    assert sample.lower.points_px[0] == (680, 325)


def test_component_and_manual_sources_cannot_be_ambiguous():
    with pytest.raises(ValueError, match="manual mode requires only manual"):
        V121TraceCapture(
            candidate_id="c", trace_region=TraceRegionV121(0, 0, 20, 20),
            upper_mode="manual", lower_mode="component", upper_component_id="ink_1",
            lower_component_id="ink_2", upper_manual=ManualPolylineV121(((0,0),(1,1),(2,1),(3,0))),
        )


def test_capture_serialization_round_trips_raw_points():
    original = _manual_capture()
    restored = load_trace_capture(trace_capture_to_json(original))
    assert restored == original


def test_nonapproved_review_cannot_be_digitized():
    pending = V120CandidateReview(candidate_id="c", source_bbox=TraceRegionV120(0,0,20,20))
    with pytest.raises(ValueError, match="approved"):
        digitize_v121_capture("unused.jpg", pending, _manual_capture())


def test_manual_trace_rejects_nonfinite_or_duplicate_points():
    with pytest.raises(ValueError, match="finite"):
        ManualPolylineV121(((0, 0), (1, float("nan")), (2, 1), (3, 0)))
    with pytest.raises(ValueError, match="duplicate"):
        ManualPolylineV121(((0, 0), (1, 1), (1, 1), (3, 0)))


def test_reserved_manual_selection_is_explicit_not_silent():
    record = _approved()
    assert record.upper_candidate_id == MANUAL_UPPER_TRACE_ID
    assert record.lower_candidate_id == MANUAL_LOWER_TRACE_ID


def test_component_mode_uses_reviewer_selected_smaller_region_on_real_source():
    source = "references/v1.10/sources/user_supplied/reference_sheet_2026-09-18.jpg"
    review = V120CandidateReview(
        candidate_id="candidate_001", source_bbox=TraceRegionV120(481, 12, 125, 96),
        eye_identification=EyeIdentification.YES, eye_side="single",
        upper_candidate_id="ink_001", lower_candidate_id="ink_002",
        medial_terminal_px=(490.0, 70.0), lateral_terminal_px=(595.0, 70.0),
        caruncle_status=CaruncleReview.UNKNOWN, epicanthus_status=EpicanthusReview.UNKNOWN,
        family=ReferenceFamily.UNCLASSIFIED, sample_id="S-001-COMP", reviewer_status=ReviewerStatus.APPROVED,
    )
    capture = V121TraceCapture(
        candidate_id="candidate_001", trace_region=TraceRegionV121(485, 18, 115, 88),
        upper_mode="component", lower_mode="component", upper_component_id="ink_001", lower_component_id="ink_002",
    )
    sample = digitize_v121_capture(source, review, capture)
    assert sample.complete_curve_digitization
    assert sample.upper.points_px[0] != sample.upper.points_px[-1]


def test_manual_sentinel_cannot_leak_into_component_digitizer():
    from visual_engine.components.face.eyes.reference import digitize_v120_review
    with pytest.raises(ValueError, match="selected trace component"):
        digitize_v120_review("references/v1.10/sources/user_supplied/reference_sheet_2026-09-18.jpg", _approved())


def test_v120_rejects_half_manual_half_component_selection():
    with pytest.raises(ValueError, match="both reserved upper/lower IDs"):
        V120CandidateReview(
            candidate_id="c", source_bbox=TraceRegionV120(0, 0, 20, 20),
            eye_identification=EyeIdentification.YES, eye_side="single",
            upper_candidate_id=MANUAL_UPPER_TRACE_ID, lower_candidate_id="ink_002",
            medial_terminal_px=(1.0, 1.0), lateral_terminal_px=(10.0, 1.0),
            caruncle_status=CaruncleReview.UNKNOWN, epicanthus_status=EpicanthusReview.UNKNOWN,
            family=ReferenceFamily.UNCLASSIFIED, sample_id="S-half", reviewer_status=ReviewerStatus.APPROVED,
        )
