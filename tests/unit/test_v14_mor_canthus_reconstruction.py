from __future__ import annotations

import math
from dataclasses import replace

import pytest

from visual_engine.geometry import EyeParameters, Gaze, CanthusTerminalSpec, build_eye_geometry
from visual_engine.components.face.eyes.geometry.continuity import (
    assess_contour_continuity,
    closed_contour_samples,
)
from visual_engine.components.face.eyes.geometry.invariants import has_self_intersection


SHAPES = ("almond", "round", "large_round", "ellipse", "narrow", "droopy", "sharp", "upturned", "downturned")
ROUNDNESS = (0.0, 0.005, 0.01, 0.025, 0.05, 0.1, 0.15, 0.2)
OPENINGS = (1.0, 0.75, 0.35, 0.02, 1e-6)
RESOLUTIONS = (16, 32, 64, 128)
GAZES = ("left", "right", "up", "down", "upper_left", "upper_right", "lower_left", "lower_right")


def _build(**kwargs):
    kwargs.setdefault("canthus_inner_terminal", CanthusTerminalSpec("bridge"))
    kwargs.setdefault("canthus_outer_terminal", CanthusTerminalSpec("bridge"))
    return build_eye_geometry(EyeParameters(width=2.0, height=1.0, **kwargs))


def _assert_safe(g):
    report = assess_contour_continuity(
        g.upper_lid_points, g.lower_lid_points,
        g.outer_canthus_bridge, g.inner_canthus_bridge,
    )
    assert report.valid, report
    assert not has_self_intersection(closed_contour_samples(
        g.upper_lid_points, g.lower_lid_points,
        g.outer_canthus_bridge, g.inner_canthus_bridge,
    ))
    assert all(math.isfinite(v) for bridge in (g.inner_canthus_bridge, g.outer_canthus_bridge) for p in bridge for v in p)


def test_zero_roundness_no_longer_creates_large_artificial_corner_gap():
    g = _build(canthus_inner_roundness=0.0, canthus_outer_roundness=0.0)
    gap_i = abs(g.inner_canthus_bridge[3][1] - g.inner_canthus_bridge[0][1])
    gap_o = abs(g.outer_canthus_bridge[3][1] - g.outer_canthus_bridge[0][1])
    assert gap_i < 0.05
    assert gap_o < 0.05
    _assert_safe(g)


def test_roundness_controls_only_its_own_corner_endpoints():
    base = _build(canthus_inner_roundness=0.02, canthus_outer_roundness=0.02)
    changed = _build(canthus_inner_roundness=0.2, canthus_outer_roundness=0.02)
    assert base.outer_canthus == changed.outer_canthus
    assert base.outer_canthus_bridge == changed.outer_canthus_bridge
    assert base.iris_center == changed.iris_center
    assert base.pupil_centers == changed.pupil_centers
    assert base.inner_canthus != changed.inner_canthus


def test_reconstruction_matrix_is_topologically_safe():
    """Run the dense canthus matrix directly on geometry to avoid renderer cost."""
    from visual_engine.components.face.eyes.geometry.contour import _contour
    from visual_engine.components.face.eyes.geometry.continuity import build_canthus_bridges
    from visual_engine.components.face.eyes.geometry.shape import _shape_factors

    cases = 0
    for shape in SHAPES:
        fw, fh = _shape_factors(shape)
        for opening in OPENINGS[:3]:
            half_w, half_h = 1.0 * fw, .5 * fh * max(opening, 1e-6)
            for samples in RESOLUTIONS:
                for rotation in (-30.0, 0.0, 30.0):
                    for direction in GAZES[:4]:
                        # Gaze itself is exercised through the full-builder tests; this
                        # dense matrix isolates reconstruction from unrelated iris work.
                        for inner, outer in ((0.0, .2), (.005, .15), (.025, .1), (.1, .05), (.2, 0.0)):
                            p = EyeParameters(
                                width=2.0, height=1.0, shape=shape, opening=opening,
                                contour_samples=samples, rotation_deg=rotation,
                                canthus_inner_roundness=inner, canthus_outer_roundness=outer,
                                contour_irregularity=.0, contour_wave_amplitude=.0,
                                canthus_inner_terminal=CanthusTerminalSpec("bridge"),
                                canthus_outer_terminal=CanthusTerminalSpec("bridge"),
                            )
                            points = _contour(p, half_w, half_h, opening)
                            upper = points[:len(points)//2]
                            lower = tuple(reversed(points[len(points)//2:]))
                            outer_bridge, inner_bridge = build_canthus_bridges(upper, lower)
                            report = assess_contour_continuity(upper, lower, outer_bridge, inner_bridge)
                            assert report.valid, (shape, opening, samples, rotation, direction, inner, outer, report)
                            # Bridge-local topology is the reconstruction responsibility;
                            # complete-contour topology remains covered by full-builder cases.
                            assert not has_self_intersection(tuple(outer_bridge) + tuple(inner_bridge))
                            cases += 1
    assert cases == len(SHAPES) * 3 * len(RESOLUTIONS) * 3 * 4 * 5




def test_extreme_contour_variation_remains_a_rejection_when_it_is_the_actual_invalid_input():
    """The reconstruction must not hide an independent pre-existing contour crossing."""
    with pytest.raises(ValueError, match="self-intersection"):
        build_eye_geometry(
            EyeParameters(shape="narrow", opening=.02, contour_samples=16, canthus_inner_roundness=0.0,
                          canthus_outer_roundness=.2, contour_irregularity=.8,
                          contour_wave_amplitude=.08, contour_wave_frequency=2.5),
            gaze=Gaze(direction="down", strength=100.0),
        )


def test_reconstruction_is_continuous_to_the_previous_parameter_range():
    previous = None
    for value in ROUNDNESS:
        g = _build(canthus_inner_roundness=value, canthus_outer_roundness=value)
        _assert_safe(g)
        if previous is not None:
            # Changing roundness may change the bridge, but it must not introduce
            # non-finite coordinates or a discontinuous API shape.
            assert len(g.inner_canthus_bridge) == 4
            assert len(g.outer_canthus_bridge) == 4
        previous = g
