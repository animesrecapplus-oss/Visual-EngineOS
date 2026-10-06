from __future__ import annotations

import math

from visual_engine.geometry import EyeParameters, Gaze, CanthusTerminalSpec, build_eye_geometry
from visual_engine.components.face.eyes.geometry.continuity import assess_contour_continuity, closed_contour_samples
from visual_engine.components.face.eyes.geometry.invariants import has_self_intersection
from visual_engine.components.face.eyes.morphology.canthus_metrics import measure_canthus


def _build(**kwargs):
    values = {"width": 2.0, "height": 1.0, "opening": .82, "canthus_inner_terminal": CanthusTerminalSpec("bridge"), "canthus_outer_terminal": CanthusTerminalSpec("bridge")}
    values.update(kwargs)
    return build_eye_geometry(EyeParameters(**values))


def _safe(g):
    report = assess_contour_continuity(g.upper_lid_points, g.lower_lid_points, g.outer_canthus_bridge, g.inner_canthus_bridge)
    assert report.valid, report
    closed = closed_contour_samples(g.upper_lid_points, g.lower_lid_points, g.outer_canthus_bridge, g.inner_canthus_bridge)
    assert not has_self_intersection(closed)
    assert all(math.isfinite(v) for p in closed for v in p)


def test_zero_transition_is_v14_compatible():
    a = _build()
    b = _build(canthus_inner_transition=0.0, canthus_outer_transition=0.0)
    assert a == b


def test_transition_does_not_move_semantic_or_internal_anchors():
    a = _build(canthus_inner_transition=0.0, canthus_outer_transition=0.0)
    b = _build(canthus_inner_transition=1.0, canthus_outer_transition=1.0)
    assert a.inner_canthus == b.inner_canthus
    assert a.outer_canthus == b.outer_canthus
    assert a.iris_center == b.iris_center
    assert a.iris_rx == b.iris_rx and a.iris_ry == b.iris_ry
    assert a.pupil_centers == b.pupil_centers
    assert a.pupil_radii == b.pupil_radii


def test_inner_and_outer_transition_are_orthogonal():
    base = _build(canthus_inner_transition=0.0, canthus_outer_transition=0.0)
    inner = _build(canthus_inner_transition=1.0, canthus_outer_transition=0.0)
    outer = _build(canthus_inner_transition=0.0, canthus_outer_transition=1.0)
    assert inner.outer_canthus_bridge == base.outer_canthus_bridge
    assert inner.inner_canthus_bridge != base.inner_canthus_bridge
    assert outer.inner_canthus_bridge == base.inner_canthus_bridge
    assert outer.outer_canthus_bridge != base.outer_canthus_bridge


def test_transition_reduces_endpoint_curvature_concentration_on_calibration_case():
    values = []
    for t in (0.0, .25, .5, .75, 1.0):
        g = _build(canthus_inner_transition=t, canthus_outer_transition=t)
        m = measure_canthus(g.inner_canthus_bridge, g.inner_canthus, g.outer_canthus)
        values.append((m.endpoint_curvature_fraction_20, m.curvature_peak_to_mean))
        _safe(g)
    assert all(values[i + 1][0] < values[i][0] for i in range(len(values) - 1))
    assert all(values[i + 1][1] < values[i][1] for i in range(len(values) - 1))


def test_boundary_and_gaze_matrix_remains_safe():
    for shape in ("almond", "round", "narrow", "upturned", "downturned"):
        for opening in (1.0, .35, .02, 1e-6):
            for t in (0.0, .5, 1.0):
                for rotation in (-30.0, 0.0, 30.0):
                    g = build_eye_geometry(
                        EyeParameters(width=2, height=1, shape=shape, opening=opening,
                                      rotation_deg=rotation, contour_samples=32,
                                      canthus_inner_transition=t, canthus_outer_transition=1.0-t,
                                      canthus_inner_terminal=CanthusTerminalSpec("bridge"), canthus_outer_terminal=CanthusTerminalSpec("bridge")),
                        gaze=Gaze(direction="upper_right", strength=.6),
                    )
                    if opening > 0:
                        _safe(g)


def test_transition_can_be_rejected_when_it_causes_real_contour_intersection():
    # This is deliberately a fail-closed case: the profile control must not hide
    # an actual topological failure in a narrow eye.
    try:
        _build(shape="narrow", opening=.35, canthus_inner_transition=.25, canthus_outer_transition=.25)
    except ValueError as exc:
        assert "self-intersection" in str(exc)
    else:
        raise AssertionError("unsafe transition was silently accepted")


def test_invalid_transition_domain_is_rejected():
    for name in ("canthus_inner_transition", "canthus_outer_transition"):
        try:
            EyeParameters(**{name: -1e-9})
        except ValueError:
            pass
        else:
            raise AssertionError(name)
        try:
            EyeParameters(**{name: 1.0000001})
        except ValueError:
            pass
        else:
            raise AssertionError(name)
