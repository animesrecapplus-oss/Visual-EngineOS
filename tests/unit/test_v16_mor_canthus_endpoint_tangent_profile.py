from __future__ import annotations

import math
import pytest

from visual_engine.geometry import CanthusEndpointTangentProfile, CanthusTerminalSpec, EyeParameters, Gaze, build_eye_geometry
from visual_engine.components.face.eyes.geometry.continuity import assess_contour_continuity, closed_contour_samples
from visual_engine.components.face.eyes.geometry.invariants import has_self_intersection


def _build(**kwargs):
    values = {"width": 2.0, "height": 1.0, "opening": .82, "contour_samples": 64, "canthus_inner_terminal": CanthusTerminalSpec("bridge"), "canthus_outer_terminal": CanthusTerminalSpec("bridge")}
    values.update(kwargs)
    return build_eye_geometry(EyeParameters(**values))


def _profile(**kwargs):
    return CanthusEndpointTangentProfile(**kwargs)


def _assert_safe(g):
    report = assess_contour_continuity(g.upper_lid_points, g.lower_lid_points, g.outer_canthus_bridge, g.inner_canthus_bridge)
    assert report.valid, report
    closed = closed_contour_samples(g.upper_lid_points, g.lower_lid_points, g.outer_canthus_bridge, g.inner_canthus_bridge, bridge_samples=33)
    assert not has_self_intersection(closed)
    assert all(math.isfinite(v) for point in closed for v in point)


def test_default_profiles_are_exact_v15_compatibility():
    a = _build()
    b = _build(
        canthus_inner_upper_profile=_profile(),
        canthus_inner_lower_profile=_profile(),
        canthus_outer_upper_profile=_profile(),
        canthus_outer_lower_profile=_profile(),
    )
    assert a == b


def test_profile_validation_is_finite_and_bounded():
    with pytest.raises(ValueError): _profile(angle_deg=float("nan"))
    with pytest.raises(ValueError): _profile(length_scale=float("inf"))
    with pytest.raises(ValueError): _profile(influence=float("nan"))
    with pytest.raises(ValueError): _profile(angle_deg=-45.00001)
    with pytest.raises(ValueError): _profile(angle_deg=45.00001)
    with pytest.raises(ValueError): _profile(length_scale=.24999)
    with pytest.raises(ValueError): _profile(length_scale=2.00001)
    with pytest.raises(ValueError): _profile(influence=-1e-9)
    with pytest.raises(ValueError): _profile(influence=1.000001)


def test_profile_must_be_the_declared_type():
    with pytest.raises(TypeError):
        EyeParameters(canthus_inner_upper_profile=object())


@pytest.mark.parametrize("field", [
    "canthus_inner_upper_profile", "canthus_inner_lower_profile",
    "canthus_outer_upper_profile", "canthus_outer_lower_profile",
])
def test_each_endpoint_can_be_changed_independently(field):
    base = _build()
    profiled = _build(**{field: _profile(angle_deg=15.0, length_scale=1.15, influence=1.0)})
    assert base.inner_canthus == profiled.inner_canthus
    assert base.outer_canthus == profiled.outer_canthus
    assert base.iris_center == profiled.iris_center
    assert base.pupil_centers == profiled.pupil_centers
    _assert_safe(profiled)


def test_inner_upper_does_not_change_outer_junction():
    base = _build()
    changed = _build(canthus_inner_upper_profile=_profile(angle_deg=20, length_scale=1.25, influence=1))
    assert changed.outer_canthus_bridge == base.outer_canthus_bridge
    assert changed.upper_lid_points[-3:] == base.upper_lid_points[-3:]


def test_inner_lower_does_not_change_outer_junction():
    base = _build()
    changed = _build(canthus_inner_lower_profile=_profile(angle_deg=-20, length_scale=.8, influence=1))
    assert changed.outer_canthus_bridge == base.outer_canthus_bridge
    assert changed.lower_lid_points[-3:] == base.lower_lid_points[-3:]


def test_outer_upper_does_not_change_inner_junction():
    base = _build()
    changed = _build(canthus_outer_upper_profile=_profile(angle_deg=-20, length_scale=1.25, influence=1))
    assert changed.inner_canthus_bridge == base.inner_canthus_bridge
    assert changed.upper_lid_points[:3] == base.upper_lid_points[:3]


def test_outer_lower_does_not_change_inner_junction():
    base = _build()
    changed = _build(canthus_outer_lower_profile=_profile(angle_deg=20, length_scale=.8, influence=1))
    assert changed.inner_canthus_bridge == base.inner_canthus_bridge
    assert changed.lower_lid_points[:3] == base.lower_lid_points[:3]


def test_influence_zero_ignores_nonzero_angle_and_length():
    base = _build()
    changed = _build(canthus_inner_upper_profile=_profile(angle_deg=45, length_scale=2, influence=0))
    assert changed == base


def test_influence_is_continuous_between_baseline_and_full_profile():
    p0 = _profile(angle_deg=20, length_scale=1.4, influence=0)
    p50 = _profile(angle_deg=20, length_scale=1.4, influence=.5)
    p100 = _profile(angle_deg=20, length_scale=1.4, influence=1)
    a = _build(canthus_inner_upper_profile=p0)
    b = _build(canthus_inner_upper_profile=p50)
    c = _build(canthus_inner_upper_profile=p100)
    assert a != b != c
    _assert_safe(b); _assert_safe(c)


@pytest.mark.parametrize("shape", ["almond", "round", "large_round", "ellipse", "narrow", "droopy", "sharp", "upturned", "downturned"])
@pytest.mark.parametrize("opening", [1.0, .82, .35, .02])
def test_shape_opening_matrix_remains_safe(shape, opening):
    g = _build(
        shape=shape, opening=opening,
        canthus_inner_upper_profile=_profile(angle_deg=5, length_scale=1.05, influence=1),
        canthus_inner_lower_profile=_profile(angle_deg=-4, length_scale=.97, influence=1),
        canthus_outer_upper_profile=_profile(angle_deg=-5, length_scale=1.03, influence=1),
        canthus_outer_lower_profile=_profile(angle_deg=4, length_scale=.98, influence=1),
    )
    if opening > 0:
        _assert_safe(g)


@pytest.mark.parametrize("rotation", [-30, -15, 0, 15, 30])
def test_rotation_preserves_profile_safety(rotation):
    g = _build(
        rotation_deg=rotation,
        canthus_inner_upper_profile=_profile(angle_deg=15, length_scale=1.15, influence=1),
        canthus_inner_lower_profile=_profile(angle_deg=-10, length_scale=.9, influence=1),
        canthus_outer_upper_profile=_profile(angle_deg=-12, length_scale=1.1, influence=1),
        canthus_outer_lower_profile=_profile(angle_deg=8, length_scale=.92, influence=1),
    )
    _assert_safe(g)


def test_diagonal_gaze_preserves_profile_safety():
    g = build_eye_geometry(
        params=EyeParameters(
            width=2, height=1, opening=.55,
            canthus_inner_upper_profile=_profile(angle_deg=5, length_scale=1.05, influence=1),
            canthus_inner_lower_profile=_profile(angle_deg=-4, length_scale=.97, influence=1),
            canthus_outer_upper_profile=_profile(angle_deg=-5, length_scale=1.03, influence=1),
            canthus_outer_lower_profile=_profile(angle_deg=4, length_scale=.98, influence=1),
        ),
        gaze=Gaze(direction="upper_right", strength=.6),
    )
    _assert_safe(g)


def test_internal_ocular_assembly_is_orthogonal_to_endpoint_profiles():
    base = _build()
    changed = _build(
        canthus_inner_upper_profile=_profile(angle_deg=20, length_scale=1.5, influence=1),
        canthus_inner_lower_profile=_profile(angle_deg=-20, length_scale=.6, influence=1),
        canthus_outer_upper_profile=_profile(angle_deg=-20, length_scale=1.5, influence=1),
        canthus_outer_lower_profile=_profile(angle_deg=20, length_scale=.6, influence=1),
    )
    assert changed.iris_center == base.iris_center
    assert changed.iris_rx == base.iris_rx and changed.iris_ry == base.iris_ry
    assert changed.pupil_centers == base.pupil_centers
    assert changed.pupil_radii == base.pupil_radii


def test_profile_changes_actual_bridge_tangent_not_only_hidden_metadata():
    base = _build()
    changed = _build(canthus_inner_upper_profile=_profile(angle_deg=25, length_scale=1.3, influence=1))
    assert changed.inner_canthus_bridge != base.inner_canthus_bridge
    # The bridge's first derivative is encoded by its first two control points.
    b0 = base.inner_canthus_bridge
    b1 = changed.inner_canthus_bridge
    # The inner bridge starts at the lower inner junction and ends at the upper
    # inner junction, so the upper profile changes the bridge's END derivative.
    v0 = (b0[3][0]-b0[2][0], b0[3][1]-b0[2][1])
    v1 = (b1[3][0]-b1[2][0], b1[3][1]-b1[2][1])
    assert not math.isclose(math.atan2(v0[1], v0[0]), math.atan2(v1[1], v1[0]), abs_tol=1e-8)


def test_length_axis_changes_tangent_magnitude_without_moving_anchor():
    base = _build()
    changed = _build(canthus_inner_upper_profile=_profile(length_scale=1.5, influence=1))
    b0, b1 = base.inner_canthus_bridge, changed.inner_canthus_bridge
    base_len = math.dist(b0[3], b0[2])
    changed_len = math.dist(b1[3], b1[2])
    assert changed_len > base_len
    assert b0[3] == b1[3]


def test_profile_is_resolved_in_eye_local_frame_before_global_rotation():
    local = _build(canthus_inner_upper_profile=_profile(angle_deg=12, influence=1))
    rotated = _build(rotation_deg=30, canthus_inner_upper_profile=_profile(angle_deg=12, influence=1))
    # Compare the endpoint-to-control vector after removing the global rotation.
    def inv_rotate(v, deg):
        a = math.radians(-deg); c, s = math.cos(a), math.sin(a)
        return (v[0]*c-v[1]*s, v[0]*s+v[1]*c)
    lv = (local.inner_canthus_bridge[3][0]-local.inner_canthus_bridge[2][0], local.inner_canthus_bridge[3][1]-local.inner_canthus_bridge[2][1])
    rv = (rotated.inner_canthus_bridge[3][0]-rotated.inner_canthus_bridge[2][0], rotated.inner_canthus_bridge[3][1]-rotated.inner_canthus_bridge[2][1])
    rv = inv_rotate(rv, 30)
    assert math.isclose(lv[0], rv[0], rel_tol=1e-9, abs_tol=1e-12)
    assert math.isclose(lv[1], rv[1], rel_tol=1e-9, abs_tol=1e-12)


def test_boundary_zero_opening_remains_degenerate_by_contract():
    g = _build(
        opening=0.0,
        canthus_inner_upper_profile=_profile(angle_deg=20, length_scale=1.4, influence=1),
        canthus_outer_lower_profile=_profile(angle_deg=-20, length_scale=.7, influence=1),
    )
    assert g.outer_canthus_bridge == ()
    assert g.inner_canthus_bridge == ()
    assert g.visible_height == 0.0
