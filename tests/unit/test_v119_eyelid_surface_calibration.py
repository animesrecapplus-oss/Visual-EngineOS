from __future__ import annotations

import pytest

from visual_engine.components.face.eyes import EyeParameters, build_eye_geometry
from visual_engine.components.face.eyes.reference import (
    fit_eyelid_surface_follow_strength,
    promote_eyelid_surface_follow_strength,
)


def test_follow_strength_is_explicit_and_default_preserves_v118_value():
    assert EyeParameters().eyelid_surface_follow_strength == pytest.approx(0.10)
    assert EyeParameters(eyelid_surface_follow_strength=0.0).eyelid_surface_follow_strength == 0.0
    with pytest.raises(ValueError):
        EyeParameters(eyelid_surface_follow_strength=1.01)


def test_follow_strength_reaches_the_actual_geometry_kernel():
    neutral = build_eye_geometry(EyeParameters(alignment_axis_rotation_deg=45, eyelid_surface_follow_strength=0.0))
    coupled = build_eye_geometry(EyeParameters(alignment_axis_rotation_deg=45, eyelid_surface_follow_strength=0.20))
    assert neutral.spherical_assembly is not None
    assert coupled.spherical_assembly is not None
    assert any(a != pytest.approx(b) for pa, pb in zip(neutral.upper_lid_points, coupled.upper_lid_points) for a, b in zip(pa, pb))
    # Semantic face anchors remain owned by the aperture and therefore unchanged.
    assert neutral.inner_canthus == pytest.approx(coupled.inner_canthus)
    assert neutral.outer_canthus == pytest.approx(coupled.outer_canthus)


def test_fit_requires_two_explicitly_approved_independent_samples():
    with pytest.raises(ValueError, match="at least two"):
        fit_eyelid_surface_follow_strength([
            {"sample_id": "a", "reviewer_status": "approved", "errors_by_strength": {"0.0": 2, "0.1": 1}},
        ])
    with pytest.raises(ValueError, match="not explicitly approved"):
        fit_eyelid_surface_follow_strength([
            {"sample_id": "a", "reviewer_status": "pending_human_review", "errors_by_strength": {"0.0": 2, "0.1": 1}},
            {"sample_id": "b", "reviewer_status": "approved", "errors_by_strength": {"0.0": 2, "0.1": 1}},
        ])


def test_fit_uses_only_values_actually_evaluated_by_all_samples():
    result = fit_eyelid_surface_follow_strength([
        {"sample_id": "a", "reviewer_status": "approved", "errors_by_strength": {"0.0": 4.0, "0.1": 2.0, "0.2": 5.0}},
        {"sample_id": "b", "reviewer_status": "approved", "errors_by_strength": {"0.0": 3.0, "0.1": 1.0, "0.2": 4.0}},
    ])
    assert result.value == pytest.approx(0.1)
    assert result.mean_error == pytest.approx(1.5)
    assert result.sample_count == 2
    assert result.status == "candidate_only"


def test_promotion_requires_explicit_human_visual_acceptance():
    candidate = fit_eyelid_surface_follow_strength([
        {"sample_id": "a", "reviewer_status": "approved", "errors_by_strength": {"0.0": 2.0, "0.1": 1.0}},
        {"sample_id": "b", "reviewer_status": "approved", "errors_by_strength": {"0.0": 3.0, "0.1": 2.0}},
    ])
    with pytest.raises(ValueError, match="human visual acceptance"):
        promote_eyelid_surface_follow_strength(candidate, human_visual_acceptance=False)
    promoted = promote_eyelid_surface_follow_strength(candidate, human_visual_acceptance=True)
    assert promoted.status == "visually_accepted"
