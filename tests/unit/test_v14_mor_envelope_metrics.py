from __future__ import annotations

import math
from dataclasses import replace

import pytest

from visual_engine.geometry import EyeParameters, Gaze, build_eye_geometry
from visual_engine.components.face.eyes.morphology.envelope import measure_envelope

SHAPES = ("almond", "round", "large_round", "ellipse", "narrow", "droopy", "sharp", "upturned", "downturned")
ROTATIONS = (-30.0, 0.0, 30.0, 90.0)
OPENINGS = (1.0, 0.5, 0.02, 1e-6)
RESOLUTIONS = (16, 32, 64, 128)


def _metrics(params: EyeParameters, gaze: Gaze | None = None):
    g = build_eye_geometry(params, gaze=gaze)
    return measure_envelope(g.upper_lid_points, g.lower_lid_points, g.inner_canthus, g.outer_canthus)


def test_envelope_metrics_are_finite_and_valid_for_all_shape_families():
    for shape in SHAPES:
        m = _metrics(EyeParameters(shape=shape, width=2.0, height=1.0, opening=.82))
        assert m.valid, m
        for name in m.__dataclass_fields__:
            value = getattr(m, name)
            if isinstance(value, float):
                assert math.isfinite(value), (shape, name, value)
        assert m.width > 0 and m.height > 0
        assert m.opening_ratio >= 0
        assert -1 <= m.opening_balance <= 1


def test_local_frame_metrics_are_invariant_to_translation_rotation_and_uniform_scale():
    baseline = _metrics(EyeParameters(shape="almond", width=2.0, height=1.0, opening=.73))
    for rotation in ROTATIONS:
        for scale in (.25, 1.0, 3.5):
            p = EyeParameters(shape="almond", width=2.0 * scale, height=1.0 * scale, opening=.73, rotation_deg=rotation)
            g = build_eye_geometry(p, center=(7.25, -3.5))
            m = measure_envelope(g.upper_lid_points, g.lower_lid_points, g.inner_canthus, g.outer_canthus)
            assert m.valid
            assert m.aspect_ratio == pytest.approx(baseline.aspect_ratio, rel=1e-10, abs=1e-12)
            assert m.opening_ratio == pytest.approx(baseline.opening_ratio, rel=1e-10, abs=1e-12)
            assert m.opening_area_ratio == pytest.approx(baseline.opening_area_ratio, rel=1e-10, abs=1e-12)
            assert m.opening_balance == pytest.approx(baseline.opening_balance, abs=1e-10)
            assert m.t_open == baseline.t_open


def test_aspect_ratio_is_undefined_for_the_explicit_closed_degenerate_state():
    g = build_eye_geometry(EyeParameters(), state="closed")
    m = measure_envelope(g.upper_lid_points, g.lower_lid_points, g.inner_canthus, g.outer_canthus)
    assert m.height == pytest.approx(0.0)
    assert m.aspect_ratio is None
    assert m.opening_max == pytest.approx(0.0)
    assert m.opening_area_ratio == pytest.approx(0.0)
    assert m.t_open is None


def test_opening_profile_is_measured_from_paired_lids_not_axis_aligned_bbox():
    g = build_eye_geometry(EyeParameters(width=2.0, height=1.0, opening=.7, rotation_deg=30))
    m = measure_envelope(g.upper_lid_points, g.lower_lid_points, g.inner_canthus, g.outer_canthus)
    assert m.valid
    assert m.opening_max > 0
    assert m.opening_ratio == pytest.approx(m.opening_max / m.width)
    # The projected local height is not allowed to silently become the world-Y bbox.
    assert m.height != pytest.approx(g.visible_height) or abs(math.sin(math.radians(30))) < 1e-12


def test_opening_balance_uses_exact_half_interval_integration_even_for_odd_samples():
    upper = ((0.0, -1.0), (0.25, -1.5), (0.5, -1.0), (0.75, -1.0), (1.0, -1.0))
    lower = ((0.0, 1.0), (0.25, 1.0), (0.5, 1.0), (0.75, 1.0), (1.0, 1.0))
    m = measure_envelope(upper, lower, upper[0], upper[-1])
    assert m.valid
    assert m.opening_balance < 0
    assert m.t_open == pytest.approx(.25)


def test_metric_resolution_stress_matrix_preserves_mathematical_bounds():
    # Resolution is a property of the sampled input, not a promise that the
    # existing geometry generator is resolution-invariant. We therefore test the
    # exact inequalities that must hold at every resolution and record convergence
    # separately in visual evidence instead of inventing a tolerance that hides
    # coarse-sampling sensitivity.
    for shape in SHAPES:
        for opening in OPENINGS:
            for rotation in ROTATIONS:
                for samples in RESOLUTIONS:
                    p = EyeParameters(
                        shape=shape, width=2.0, height=1.0, opening=opening,
                        rotation_deg=rotation, contour_samples=samples,
                        upper_curve=1.17, lower_curve=.83,
                        asymmetry=.31, contour_wave_amplitude=.04,
                        contour_wave_frequency=1.7, contour_irregularity=.5,
                        canthus_inner_roundness=.18, canthus_outer_roundness=.04,
                    )
                    m = _metrics(p, Gaze(direction="upper_right", strength=.8))
                    assert m.valid, (shape, opening, rotation, samples, m)
                    assert 0 <= m.opening_area_ratio <= m.opening_ratio + 1e-12
                    assert -1 <= m.opening_balance <= 1
                    assert m.t_open is None or 0 <= m.t_open <= 1
                    assert m.u_open is None or math.isfinite(m.u_open)


def test_parameter_axes_change_the_expected_envelope_measurements_without_reconstructing_metrics():
    base = _metrics(EyeParameters(width=2.0, height=1.0, opening=.8))
    taller = _metrics(EyeParameters(width=2.0, height=1.25, opening=.8))
    wider = _metrics(EyeParameters(width=2.5, height=1.0, opening=.8))
    closed = _metrics(EyeParameters(width=2.0, height=1.0, opening=.02))
    assert taller.aspect_ratio < base.aspect_ratio
    assert wider.aspect_ratio > base.aspect_ratio
    assert closed.opening_ratio < base.opening_ratio
    assert closed.opening_area_ratio < base.opening_area_ratio


def test_malformed_envelope_fails_closed_instead_of_being_repaired():
    with pytest.raises(ValueError):
        measure_envelope(((0.0, 0.0),), ((0.0, 1.0),), (0.0, 0.0), (1.0, 0.0))
    with pytest.raises(ValueError):
        measure_envelope(((0.0, 0.0), (float("nan"), 0.0)), ((0.0, 1.0), (1.0, 1.0)), (0.0, 0.0), (1.0, 0.0))
    with pytest.raises(ValueError):
        measure_envelope(((0.0, 0.0), (1.0, 0.0)), ((0.0, 1.0), (1.0, 1.0)), (0.0, 0.0), (0.0, 0.0))
