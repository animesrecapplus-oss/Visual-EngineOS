import math

import pytest

from visual_engine.geometry import EyeParameters, Gaze, CanthusTerminalSpec, build_eye_geometry
from visual_engine.components.face.eyes.geometry.continuity import (
    assess_contour_continuity,
    closed_contour_samples,
)
from visual_engine.components.face.eyes.geometry.invariants import has_self_intersection
from visual_engine.render import eye_outer_path


SHAPES = ("almond", "round", "large_round", "ellipse", "narrow", "droopy", "sharp", "upturned", "downturned")
DIRECTIONS = ("left", "right", "up", "down", "upper_left", "upper_right", "lower_left", "lower_right")


def _bridge_params(**kwargs):
    kwargs.setdefault("canthus_inner_terminal", CanthusTerminalSpec("bridge"))
    kwargs.setdefault("canthus_outer_terminal", CanthusTerminalSpec("bridge"))
    return EyeParameters(**kwargs)


def _assert_continuous(g):
    report = assess_contour_continuity(
        g.upper_lid_points, g.lower_lid_points,
        g.outer_canthus_bridge, g.inner_canthus_bridge,
    )
    assert report.valid, report
    # Floating-point derivative reconstruction has an absolute machine floor.
    # Keep the test relative where geometry is large, but do not reject valid
    # micro-scale geometry because subtraction rounds at ~1e-16.
    assert report.max_error <= max(1e-9 * max(report.min_tangent_norm, 1e-15), 1e-15)
    assert report.min_tangent_norm > 1e-12
    samples = closed_contour_samples(
        g.upper_lid_points, g.lower_lid_points,
        g.outer_canthus_bridge, g.inner_canthus_bridge,
    )
    assert not has_self_intersection(samples)


def test_c1_continuity_is_exact_at_both_canthus_joins():
    g = build_eye_geometry(EyeParameters(width=2.0, height=1.0, canthus_inner_roundness=.18, canthus_outer_roundness=.03, canthus_inner_terminal=CanthusTerminalSpec("bridge"), canthus_outer_terminal=CanthusTerminalSpec("bridge")))
    _assert_continuous(g)
    assert g.outer_canthus_bridge[0] == g.upper_lid_points[-1]
    assert g.outer_canthus_bridge[3] == g.lower_lid_points[-1]
    assert g.inner_canthus_bridge[0] == g.lower_lid_points[0]
    assert g.inner_canthus_bridge[3] == g.upper_lid_points[0]


def test_continuity_survives_shape_opening_resolution_and_gaze_variation():
    for shape in SHAPES:
        for opening in (1.0, 0.5, 0.02, 1e-6):
            for samples in (16, 32, 64, 128):
                for direction in ("upper_right", "lower_left"):
                    g = build_eye_geometry(
                        EyeParameters(
                            shape=shape, width=2.0, height=1.0, opening=opening,
                            contour_samples=samples,
                            canthus_inner_roundness=.2,
                            canthus_outer_roundness=.0,
                            canthus_inner_terminal=CanthusTerminalSpec("bridge"),
                            canthus_outer_terminal=CanthusTerminalSpec("bridge"),
                        ),
                        gaze=Gaze(direction=direction, strength=1.0),
                    )
                    _assert_continuous(g)


def test_continuity_survives_all_gaze_directions_and_rotation():
    for direction in DIRECTIONS:
        for rotation in (-30.0, 0.0, 30.0, 90.0):
            g = build_eye_geometry(
                EyeParameters(rotation_deg=rotation, canthus_inner_roundness=.2, canthus_outer_roundness=.2, canthus_inner_terminal=CanthusTerminalSpec("bridge"), canthus_outer_terminal=CanthusTerminalSpec("bridge")),
                gaze=Gaze(direction=direction, strength=100.0),
            )
            _assert_continuous(g)


def test_continuity_is_rechecked_after_gaze_follow_not_only_before_it():
    base = build_eye_geometry(EyeParameters(canthus_inner_terminal=CanthusTerminalSpec("bridge"), canthus_outer_terminal=CanthusTerminalSpec("bridge")), gaze=Gaze(direction="down", strength=0.0))
    followed = build_eye_geometry(EyeParameters(canthus_inner_terminal=CanthusTerminalSpec("bridge"), canthus_outer_terminal=CanthusTerminalSpec("bridge")), gaze=Gaze(direction="down", strength=100.0))
    _assert_continuous(base)
    _assert_continuous(followed)
    assert followed.upper_lid_points != base.upper_lid_points
    assert followed.outer_canthus_bridge != base.outer_canthus_bridge


def test_self_intersection_tolerance_is_scale_relative_at_small_opening():
    g = build_eye_geometry(
        EyeParameters(opening=1e-6, canthus_inner_roundness=.2, canthus_outer_roundness=0.0, canthus_inner_terminal=CanthusTerminalSpec("bridge"), canthus_outer_terminal=CanthusTerminalSpec("bridge")),
        gaze=Gaze(direction="upper_right"),
    )
    samples = closed_contour_samples(
        g.upper_lid_points, g.lower_lid_points,
        g.outer_canthus_bridge, g.inner_canthus_bridge,
    )
    assert not has_self_intersection(samples)


def test_continuity_tangent_threshold_scales_with_geometry():
    g = build_eye_geometry(EyeParameters(width=1e-9, height=5.5e-10, opening=.5))
    _assert_continuous(g)


def test_opening_tends_to_zero_without_a_discrete_continuity_failure():
    openings = (1.0, .5, .1, .01, .001, 1e-6)
    previous = None
    for opening in openings:
        g = build_eye_geometry(EyeParameters(opening=opening), gaze=Gaze(direction="up", strength=1.0))
        _assert_continuous(g)
        if previous is not None:
            assert all(math.isfinite(v) for point in g.outer_canthus_bridge for v in point)
        previous = g
    closed = build_eye_geometry(EyeParameters(), state="closed")
    assert closed.outer_canthus_bridge == ()
    assert closed.inner_canthus_bridge == ()


def test_closed_eye_is_an_explicit_degenerate_boundary_not_a_false_c1_claim():
    g = build_eye_geometry(EyeParameters(), state="closed")
    assert g.visible_height == pytest.approx(0.0)
    assert g.outer_canthus_bridge == ()
    assert g.inner_canthus_bridge == ()


def test_renderer_serializes_geometry_owned_canthus_bridges():
    g = build_eye_geometry(_bridge_params(canthus_inner_roundness=.0, canthus_outer_roundness=.2))
    path = eye_outer_path(g)
    for point in (g.outer_canthus_bridge[1], g.outer_canthus_bridge[2], g.inner_canthus_bridge[1], g.inner_canthus_bridge[2]):
        assert f"{point[0]:.6f},{point[1]:.6f}" in path


def test_malformed_bridge_is_rejected_by_the_continuity_contract():
    g = build_eye_geometry(_bridge_params())
    bad = list(g.outer_canthus_bridge)
    bad[1] = (bad[1][0] + 0.5, bad[1][1] + 0.5)
    report = assess_contour_continuity(
        g.upper_lid_points, g.lower_lid_points, tuple(bad), g.inner_canthus_bridge,
    )
    assert not report.valid
    assert report.outer_start_error > 1e-3
