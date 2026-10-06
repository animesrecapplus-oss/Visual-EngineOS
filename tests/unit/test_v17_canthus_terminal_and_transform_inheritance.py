from __future__ import annotations

import math
import re

import pytest

from visual_engine.geometry import (
    CanthusEndpointTangentProfile,
    CanthusTerminalSpec,
    EyeAppearance,
    EyePairSpec,
    EyeParameters,
    Gaze,
    BrowSpec,
    build_eye_geometry,
    build_eye_pair,
)
from visual_engine.render import eye_outer_path, render_eye_svg


def _default():
    return build_eye_geometry(EyeParameters(width=2.0, height=1.0))


def _bridge_params(**kwargs):
    kwargs.setdefault("canthus_inner_terminal", CanthusTerminalSpec("bridge"))
    kwargs.setdefault("canthus_outer_terminal", CanthusTerminalSpec("bridge"))
    return EyeParameters(width=2.0, height=1.0, **kwargs)


def test_v17_default_uses_shared_terminal_points_and_no_bridge_caps():
    g = _default()
    assert g.inner_canthus_bridge == ()
    assert g.outer_canthus_bridge == ()
    assert g.upper_lid_points[0] == g.lower_lid_points[0]
    assert g.upper_lid_points[-1] == g.lower_lid_points[-1]
    path = eye_outer_path(g)
    assert path.endswith(f"L {g.upper_lid_points[0][0]:.6f},{g.upper_lid_points[0][1]:.6f} Z")


def test_legacy_bridge_mode_remains_explicitly_available():
    g = build_eye_geometry(_bridge_params(canthus_inner_roundness=.12, canthus_outer_roundness=.08))
    assert len(g.inner_canthus_bridge) == 4
    assert len(g.outer_canthus_bridge) == 4
    path = eye_outer_path(g)
    assert f"{g.inner_canthus_bridge[1][0]:.6f},{g.inner_canthus_bridge[1][1]:.6f}" in path


def test_roundness_no_longer_reintroduces_a_shared_terminal_gap():
    base = _default()
    changed = build_eye_geometry(EyeParameters(width=2.0, height=1.0, canthus_inner_roundness=.2, canthus_outer_roundness=.2))
    assert changed.inner_canthus == base.inner_canthus
    assert changed.outer_canthus == base.outer_canthus
    assert changed.inner_canthus_bridge == ()
    assert changed.outer_canthus_bridge == ()


def test_only_medial_corner_gets_a_caruncle_in_a_single_eye():
    g = _default()
    assert g.medial_caruncle_points
    inner_x = g.inner_canthus[0]
    outer_x = g.outer_canthus[0]
    cx = sum(x for x, _ in g.medial_caruncle_points) / len(g.medial_caruncle_points)
    assert abs(cx - g.center_x) < abs(inner_x - g.center_x)
    assert abs(cx - g.center_x) < abs(outer_x - g.center_x)


def test_caruncle_is_disableable_without_changing_lid_geometry():
    base = _default()
    appearance = EyeAppearance()
    off = EyeAppearance(caruncle=__import__("dataclasses").replace(appearance.caruncle, enabled=False))
    changed = build_eye_geometry(EyeParameters(width=2.0, height=1.0), appearance=off)
    assert changed.medial_caruncle_points == ()
    assert changed.upper_lid_points == base.upper_lid_points
    assert changed.lower_lid_points == base.lower_lid_points


def test_caruncle_is_curved_and_not_a_four_point_closure_bridge():
    g = _default()
    pts = g.medial_caruncle_points
    assert len(pts) >= 6
    # The sampled side is not a single straight segment: at least one midpoint
    # departs from the chord joining its local neighbours.
    turns = []
    for a, b, c in zip(pts, pts[1:], pts[2:]):
        turns.append((b[0]-a[0])*(c[1]-b[1]) - (b[1]-a[1])*(c[0]-b[0]))
    assert any(abs(v) > 1e-12 for v in turns)


def test_image_left_and_image_right_have_medial_canthus_toward_pair_center():
    pair = build_eye_pair(EyePairSpec())
    assert pair.left.inner_canthus[0] > pair.left.outer_canthus[0]
    assert pair.right.inner_canthus[0] < pair.right.outer_canthus[0]
    left_caruncle_x = sum(x for x, _ in pair.left.medial_caruncle_points) / len(pair.left.medial_caruncle_points)
    right_caruncle_x = sum(x for x, _ in pair.right.medial_caruncle_points) / len(pair.right.medial_caruncle_points)
    assert left_caruncle_x > pair.left.center_x
    assert right_caruncle_x < pair.right.center_x


def test_outer_corner_has_no_medial_detail():
    pair = build_eye_pair(EyePairSpec())
    for g in (pair.left, pair.right):
        assert g.medial_caruncle_points
        assert all(abs(x - g.outer_canthus[0]) > 1e-6 or abs(y - g.outer_canthus[1]) > 1e-6 for x, y in g.medial_caruncle_points)


def test_parent_rotation_is_separate_from_gaze_direction():
    gaze = Gaze(direction="upper_right", strength=1.0)
    a = build_eye_geometry(EyeParameters(rotation_deg=0), gaze=gaze)
    b = build_eye_geometry(EyeParameters(rotation_deg=30), gaze=gaze)
    assert a.gaze_solution.normalized_x == pytest.approx(b.gaze_solution.normalized_x)
    assert a.gaze_solution.normalized_y == pytest.approx(b.gaze_solution.normalized_y)
    assert b.rotation_deg == 30


def test_actual_gaze_moves_internal_assembly_without_rotating_parent_envelope():
    center = build_eye_geometry(EyeParameters(rotation_deg=0), gaze=Gaze(direction="center", strength=0.0))
    aimed = build_eye_geometry(EyeParameters(rotation_deg=0), gaze=Gaze(direction="upper_right", strength=1.0))
    assert center.rotation_deg == aimed.rotation_deg == 0
    assert center.iris_center != aimed.iris_center
    assert center.inner_canthus == aimed.inner_canthus
    assert center.outer_canthus == pytest.approx(aimed.outer_canthus)


def test_parent_rotation_is_inherited_by_brow_renderer():
    appearance = EyeAppearance(eyebrow=BrowSpec(enabled=True, angle_deg=0.0, y=-.4))
    g = build_eye_geometry(EyeParameters(rotation_deg=30), appearance=appearance)
    svg = render_eye_svg(g, appearance=appearance)
    assert 'rotate(30.000000)' in svg


def test_brow_angle_is_parent_rotation_plus_local_brow_angle():
    appearance = EyeAppearance(eyebrow=BrowSpec(enabled=True, angle_deg=7.5, y=-.4))
    g = build_eye_geometry(EyeParameters(rotation_deg=30), appearance=appearance)
    svg = render_eye_svg(g, appearance=appearance)
    assert 'rotate(37.500000)' in svg


def test_brow_is_not_rotated_by_gaze_direction():
    appearance = EyeAppearance(eyebrow=BrowSpec(enabled=True, angle_deg=0.0, y=-.4))
    g = build_eye_geometry(EyeParameters(rotation_deg=0), appearance=appearance, gaze=Gaze(direction="upper_right", strength=1.0))
    svg = render_eye_svg(g, appearance=appearance)
    assert 'rotate(0.000000)' in svg


def test_endpoint_profiles_remain_real_geometry_under_shared_terminal_topology():
    base = _default()
    changed = build_eye_geometry(EyeParameters(
        width=2.0, height=1.0,
        canthus_inner_upper_profile=CanthusEndpointTangentProfile(angle_deg=15, length_scale=1.4, influence=1),
    ))
    assert changed.inner_canthus == base.inner_canthus
    assert changed.outer_canthus == base.outer_canthus
    assert changed.upper_lid_points[1] != base.upper_lid_points[1]
    assert changed.inner_canthus_bridge == ()


def test_bridge_topology_preserves_c1_when_explicitly_requested():
    g = build_eye_geometry(_bridge_params())
    from visual_engine.components.face.eyes.geometry.continuity import assess_contour_continuity
    report = assess_contour_continuity(g.upper_lid_points, g.lower_lid_points, g.outer_canthus_bridge, g.inner_canthus_bridge)
    assert report.valid
    assert report.tangent_continuous


def test_shared_topology_does_not_claim_bridge_c1():
    g = _default()
    from visual_engine.components.face.eyes.geometry.continuity import assess_contour_continuity
    report = assess_contour_continuity(g.upper_lid_points, g.lower_lid_points, g.outer_canthus_bridge, g.inner_canthus_bridge)
    assert report.valid
    assert not report.tangent_continuous
    assert not report.c1_bridges_present
