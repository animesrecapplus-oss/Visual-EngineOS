from __future__ import annotations

import json
import math
from pathlib import Path

import pytest
from PIL import Image, ImageDraw

from visual_engine.components.face.eyes.reference import (
    CandidateReview, ReferenceFamily, ReferenceSample, ReferenceCurve, ReviewerStatus,
    ReviewManifest, apply_review_decision, caruncle_metrics, canthus_pixel_metrics,
    epicanthus_status, mor_ranges, resolve_terminals, review_from_segmentation,
    trace_component_candidates, TraceRegion, digitize_approved_eye,
    inspect_image_metadata,
)

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "references/v1.10/sources/user_supplied/reference_sheet_2026-09-18.jpg"
SEG = ROOT / "src/visual_engine/components/face/eyes/reference/V1.10_SEGMENTATION_REVIEW.json"


def _sample() -> ReferenceSample:
    return ReferenceSample(
        "s", ReferenceFamily.ANIME_STYLIZED,
        upper=ReferenceCurve("upper", ((10, 30), (20, 20), (40, 18), (70, 30))),
        lower=ReferenceCurve("lower", ((10, 30), (20, 40), (40, 42), (70, 30))),
        medial_terminal_px=(10, 30), lateral_terminal_px=(70, 30),
    )


def test_all_28_candidates_have_explicit_review_records():
    payload = json.loads(SEG.read_text(encoding="utf-8"))
    manifest = review_from_segmentation(payload, source_sha256=payload["source_sha256"])
    assert len(manifest.candidates) == 28
    assert len(manifest.approved) == 0
    assert all(c.reviewer_status == ReviewerStatus.PENDING and c.sample_id is None for c in manifest.candidates)


def test_review_decision_is_immutable_and_approval_requires_sample_id():
    manifest = ReviewManifest("V1.11", "source", "a" * 64, (CandidateReview("c1", None, "r"),))
    with pytest.raises(ValueError):
        apply_review_decision(manifest, "c1", status=ReviewerStatus.APPROVED)
    approved = apply_review_decision(manifest, "c1", status=ReviewerStatus.APPROVED, sample_id="sample_1")
    assert manifest.approved == ()
    assert approved.approved[0].sample_id == "sample_1"


def test_terminal_roles_are_semantic_not_guessed_from_eye_side():
    left = resolve_terminals(inner_px=(70, 30), outer_px=(10, 30), side="image_left")
    right = resolve_terminals(inner_px=(10, 30), outer_px=(70, 30), side="image_right")
    assert left.medial_px == (70, 30) and right.medial_px == (10, 30)
    with pytest.raises(ValueError):
        resolve_terminals(inner_px=(10, 30), outer_px=(70, 30), side="image_left")
    oblique = resolve_terminals(inner_px=(20, 30), outer_px=(10, 31), side="image_left", allow_oblique=True)
    assert oblique.medial_px == (20, 30)


def test_pixel_canthus_metrics_keep_four_endpoints_independent():
    result = canthus_pixel_metrics(_sample())
    assert "start" in result["upper"] and "end" in result["upper"]
    assert "start" in result["lower"] and "end" in result["lower"]
    assert result["terminal_distance_px"] == pytest.approx(60)
    assert result["medial_convergence_angle_deg"] > 0


def test_caruncle_and_epicanthus_never_get_invented():
    sample = _sample()
    assert caruncle_metrics(sample) is None
    assert epicanthus_status(sample, reviewer_status="unknown")["curve"] is None
    assert epicanthus_status(sample, reviewer_status="absent")["status"] == "absent"


def test_mor_ranges_require_two_samples_and_report_coverage_confidence_only():
    a = {"sample_id": "a", "canthus": {"terminal_distance_px": 20.0}}
    with pytest.raises(ValueError):
        mor_ranges([a], field_paths=("canthus.terminal_distance_px",))
    result = mor_ranges([a, {"sample_id": "b", "canthus": {"terminal_distance_px": 30.0}}], field_paths=("canthus.terminal_distance_px",))
    assert result["canthus.terminal_distance_px"]["observed_min"] == 20
    assert result["canthus.terminal_distance_px"]["observed_max"] == 30
    assert "not an anatomical" in result["canthus.terminal_distance_px"]["confidence_definition"]


def test_orientation_independent_trace_handles_vertical_stroke(tmp_path):
    source = tmp_path / "vertical.png"
    im = Image.new("RGB", (60, 90), "white")
    d = ImageDraw.Draw(im)
    d.line((30, 10, 30, 80), fill="black", width=5)
    im.save(source)
    region = TraceRegion(0, 0, 60, 90, "vertical")
    result = trace_component_candidates(source, region)
    assert result["candidate_count"] == 1
    points = result["candidates"][0]["points_px"]
    assert len(points) >= 4
    assert max(p[1] for p in points) - min(p[1] for p in points) > 50


def test_approved_digitization_orients_curves_from_inner_terminal(tmp_path):
    source = tmp_path / "eye.png"
    im = Image.new("RGB", (100, 60), "white")
    d = ImageDraw.Draw(im)
    d.line((10, 25, 90, 15), fill="black", width=3)
    d.line((10, 35, 90, 50), fill="black", width=3)
    im.save(source)
    region = TraceRegion(0, 0, 100, 60, "sample", approved=True)
    candidates = trace_component_candidates(source, region)
    assert candidates["candidate_count"] >= 2
    ids = [c["candidate_id"] for c in candidates["candidates"]]
    sample = digitize_approved_eye(source, region, family=ReferenceFamily.ANIME_STYLIZED,
                                   upper_candidate_id=ids[0], lower_candidate_id=ids[1],
                                   inner_terminal_px=(10, 25), outer_terminal_px=(90, 15))
    assert sample.upper and sample.lower
    assert math.dist(sample.upper.points_px[0], (10, 30)) < math.dist(sample.upper.points_px[-1], (10, 30))


def test_source_metadata_is_exact_and_review_artifact_uses_same_pixels():
    meta = inspect_image_metadata(SOURCE)
    assert meta["width_px"] == 792 and meta["height_px"] == 792 and meta["format"] == "JPEG"
    assert meta["sha256"] == "7bff12532250d95020b022436253dc2664acb3c58745ae715da58ae1d48adec2"
