import math

import pytest

from visual_engine.geometry import EyeParameters, Gaze, CanthusTerminalSpec, build_eye_geometry
from visual_engine.components.face.eyes.morphology.canthus_metrics import measure_canthus


def _reference_gl(c, n=256):
    # Independent high-order oracle used only in tests; production code uses its
    # fixed 128-node table. Keeping the oracle separate catches quadrature bugs.
    nodes, weights = [], []
    for k in range(1, n // 2 + 1):
        z = math.cos(math.pi * (k - .25) / (n + .5))
        for _ in range(20):
            p0, p1 = 1.0, z
            for degree in range(2, n + 1):
                p0, p1 = p1, ((2*degree-1)*z*p1-(degree-1)*p0)/degree
            derivative = n * (z*p1-p0) / (z*z-1.0)
            delta = p1 / derivative
            z -= delta
            if abs(delta) < 1e-15:
                break
        x = (1-z)/2
        w = 1/((1-z*z)*derivative*derivative)
        nodes.extend((x, 1-x)); weights.extend((w, w))
    p0,p1,p2,p3=c
    def values(t):
        u=1-t
        dx=3*(u*u*(p1[0]-p0[0])+2*u*t*(p2[0]-p1[0])+t*t*(p3[0]-p2[0]))
        dy=3*(u*u*(p1[1]-p0[1])+2*u*t*(p2[1]-p1[1])+t*t*(p3[1]-p2[1]))
        ddx=6*(u*(p2[0]-2*p1[0]+p0[0])+t*(p3[0]-2*p2[0]+p1[0]))
        ddy=6*(u*(p2[1]-2*p1[1]+p0[1])+t*(p3[1]-2*p2[1]+p1[1]))
        speed=math.hypot(dx,dy)
        return speed, abs((dx*ddy-dy*ddx)/speed**3)*speed
    arc=turn=0.0
    for t,w in zip(nodes,weights):
        speed,curv_ds=values(t); arc += w*speed; turn += w*curv_ds
    return arc,turn


def _metrics(shape="almond", rotation=0.0, opening=.82):
    g = build_eye_geometry(
        EyeParameters(shape=shape, width=2.0, height=1.0, opening=opening,
                      rotation_deg=rotation, canthus_inner_roundness=.18,
                      canthus_outer_roundness=.04,
                      canthus_inner_terminal=CanthusTerminalSpec("bridge"),
                      canthus_outer_terminal=CanthusTerminalSpec("bridge")),
        gaze=Gaze(direction="upper_right", strength=.6),
    )
    return g, measure_canthus(g.inner_canthus_bridge, g.inner_canthus, g.outer_canthus)


def test_straight_bridge_has_zero_curvature_and_unit_arc_ratio():
    c = ((0.0, 0.0), (1/3, 0.0), (2/3, 0.0), (1.0, 0.0))
    m = measure_canthus(c, (0.0, -1.0), (1.0, -1.0))
    assert m.valid
    assert m.arc_to_chord_ratio == pytest.approx(1.0, abs=1e-10)
    assert m.total_abs_turning_rad == pytest.approx(0.0, abs=1e-10)
    assert m.max_curvature == pytest.approx(0.0, abs=1e-10)
    assert m.triangle_evidence == pytest.approx(0.0, abs=1e-12)


def test_current_bridges_expose_non_simple_turning_instead_of_hiding_it():
    for shape in ("almond", "round", "narrow", "upturned", "downturned"):
        g, m = _metrics(shape)
        assert m.valid
        assert m.total_abs_turning_rad >= abs(m.net_turn_angle_rad)
        assert 0.0 <= m.turning_efficiency <= 1.0
        assert 0.0 <= m.endpoint_curvature_fraction_20 <= 1.0
        assert 0.0 <= m.half_turn_window_ratio <= 1.0
        assert m.max_chord_deviation_ratio >= 0.0
        assert m.curvature_sign_changes >= 0
        assert all(math.isfinite(v) for v in (
            m.arc_length, m.total_abs_turning_rad, m.triangle_evidence,
        ))


def test_metrics_are_invariant_to_uniform_scale_and_rigid_rotation():
    base_bridge = ((0.0, 0.10), (0.02, 0.14), (0.02, -0.14), (0.0, -0.10))
    base = measure_canthus(base_bridge, (-1.0, 0.10), (1.0, 0.10))
    angle = math.radians(30.0)
    scale = 3.5
    ca, sa = math.cos(angle), math.sin(angle)
    def transform(p):
        x, y = p
        return (4.0 + scale*(ca*x-sa*y), -2.0 + scale*(sa*x+ca*y))
    moved_bridge = tuple(transform(p) for p in base_bridge)
    moved = measure_canthus(moved_bridge, transform((-1.0, 0.10)), transform((1.0, 0.10)))
    for a, b in (
        (base.arc_to_chord_ratio, moved.arc_to_chord_ratio),
        (base.normalized_arc_length, moved.normalized_arc_length),
        (base.total_abs_turning_rad, moved.total_abs_turning_rad),
        (base.turning_efficiency, moved.turning_efficiency),
        (base.min_speed_ratio, moved.min_speed_ratio),
        (base.endpoint_curvature_fraction_20, moved.endpoint_curvature_fraction_20),
        (base.half_turn_window_ratio, moved.half_turn_window_ratio),
        (base.max_chord_deviation_ratio, moved.max_chord_deviation_ratio),
        (base.triangle_evidence, moved.triangle_evidence),
    ):
        assert a == pytest.approx(b, rel=2e-6, abs=2e-8)
    assert moved.tangent_start_angle_rad == pytest.approx(base.tangent_start_angle_rad, abs=2e-6)
    assert moved.tangent_end_angle_rad == pytest.approx(base.tangent_end_angle_rad, abs=2e-6)


def test_fixed_quadrature_matches_independent_256_node_oracle():
    g, m = _metrics("narrow")
    arc_ref, turn_ref = _reference_gl(g.inner_canthus_bridge)
    assert m.arc_length == pytest.approx(arc_ref, rel=2e-9, abs=2e-10)
    assert m.total_abs_turning_rad == pytest.approx(turn_ref, rel=2e-9, abs=2e-10)


def test_diagnostic_sampling_converges_for_distribution_metrics():
    g, low = _metrics("narrow")
    mid = measure_canthus(g.inner_canthus_bridge, g.inner_canthus, g.outer_canthus, samples=513)
    high = measure_canthus(g.inner_canthus_bridge, g.inner_canthus, g.outer_canthus, samples=1025)
    for a, b in ((low.arc_length, mid.arc_length), (mid.arc_length, high.arc_length),
                 (low.total_abs_turning_rad, mid.total_abs_turning_rad),
                 (mid.total_abs_turning_rad, high.total_abs_turning_rad)):
        assert a == pytest.approx(b, rel=2e-6, abs=2e-8)
    assert abs(mid.triangle_evidence - high.triangle_evidence) < 0.01


def test_invalid_zero_speed_and_bad_sampling_are_rejected():
    with pytest.raises(ValueError):
        measure_canthus(((0.0, 0.0),) * 4, (0.0, -1.0), (1.0, -1.0))
    g, _ = _metrics()
    with pytest.raises(ValueError):
        measure_canthus(g.inner_canthus_bridge, g.inner_canthus, g.outer_canthus, samples=32)
    with pytest.raises(ValueError):
        measure_canthus(g.inner_canthus_bridge, g.inner_canthus, g.outer_canthus, samples=64)


def test_triangle_evidence_is_a_calibration_signal_not_a_binary_verdict():
    _, m = _metrics("round")
    assert 0.0 <= m.triangle_evidence <= 1.0
    # No binary acceptance threshold is embedded in the metric layer: a future
    # threshold must come from digitized reference curves and visual review.
