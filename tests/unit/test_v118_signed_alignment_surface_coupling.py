from __future__ import annotations

import math
import pytest

from visual_engine.components.face.eyes import EyeParameters, EyePairPolicy, build_eye_geometry, build_eye_pair
from visual_engine.components.face.eyes.geometry.alignment_surface_coupling import couple_lid_curve
from visual_engine.components.face.eyes.geometry.view_axis import OcularPose3D, compose_ocular_basis


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _dist(a, b):
    return math.dist(a, b)


def test_neutral_alignment_is_exactly_the_unchanged_aperture():
    base = build_eye_geometry(EyeParameters(alignment_axis_rotation_deg=0))
    assert base.spherical_assembly is None
    for p in base.upper_lid_points + base.lower_lid_points:
        assert all(math.isfinite(v) for v in p)


def test_positive_alignment_moves_iris_in_expected_svg_y_direction_after_frame_fix():
    positive = build_eye_geometry(EyeParameters(alignment_axis_rotation_deg=30))
    negative = build_eye_geometry(EyeParameters(alignment_axis_rotation_deg=-30))
    assert positive.spherical_assembly is not None
    assert negative.spherical_assembly is not None
    assert positive.spherical_assembly.iris_projected_center[1] > 0
    assert negative.spherical_assembly.iris_projected_center[1] < 0


def test_alignment_changes_lid_interior_but_not_semantic_canthus_anchors():
    base = build_eye_geometry(EyeParameters(alignment_axis_rotation_deg=0))
    positive = build_eye_geometry(EyeParameters(alignment_axis_rotation_deg=45))
    negative = build_eye_geometry(EyeParameters(alignment_axis_rotation_deg=-45))
    for candidate in (positive, negative):
        assert candidate.inner_canthus == pytest.approx(base.inner_canthus)
        assert candidate.outer_canthus == pytest.approx(base.outer_canthus)
        assert candidate.upper_lid_points[0] == pytest.approx(base.upper_lid_points[0])
        assert candidate.upper_lid_points[-1] == pytest.approx(base.upper_lid_points[-1])
        assert candidate.lower_lid_points[0] == pytest.approx(base.lower_lid_points[0])
        assert candidate.lower_lid_points[-1] == pytest.approx(base.lower_lid_points[-1])
        assert any(abs(a-b) > 1e-8 for pa, pb in zip(candidate.upper_lid_points, base.upper_lid_points) for a, b in zip(pa, pb))


def test_pupil_is_still_a_child_of_the_rotated_iris_surface():
    for deg in (-75, -45, 30, 60, 75):
        g = build_eye_geometry(EyeParameters(alignment_axis_rotation_deg=deg))
        a = g.spherical_assembly
        assert a is not None and a.iris_attachment is not None and a.pupil_attachments
        c, r = a.center, a.radius
        assert _dist(c, a.iris_surface_center) == pytest.approx(r, rel=1e-7, abs=1e-8)
        assert _dist(c, a.pupil_surface_center) == pytest.approx(r, rel=1e-7, abs=1e-8)
        # The child tangent frame remains finite and orthogonal to its surface normal.
        child = a.pupil_attachments[0]
        assert abs(_dot(child.normal, child.tangent_x)) < 1e-8
        assert abs(_dot(child.normal, child.tangent_y)) < 1e-8


def test_both_alignment_signs_change_the_aperture_without_screen_roll():
    base = build_eye_geometry(EyeParameters(alignment_axis_rotation_deg=0, rotation_deg=0))
    for deg in (-60, 60):
        g = build_eye_geometry(EyeParameters(alignment_axis_rotation_deg=deg, rotation_deg=0))
        assert g.rotation_deg == 0
        assert g.alignment_axis_rotation_deg == deg
        assert g.spherical_assembly.alignment_coupling.sign == ("alignment_positive" if deg > 0 else "alignment_negative")


def test_parent_alignment_is_inherited_without_replacing_local_sign():
    parent = compose_ocular_basis(pose=OcularPose3D(alignment_axis_rotation_deg=20))
    child = compose_ocular_basis(parent, OcularPose3D(alignment_axis_rotation_deg=-10))
    assert abs(_dot(child.alignment_axis, child.vertical_axis)) < 1e-8
    assert abs(_dot(child.alignment_axis, child.view_axis)) < 1e-8
    assert abs(_dot(child.vertical_axis, child.view_axis)) < 1e-8


def test_lid_surface_coupling_is_endpoint_safe_and_finite():
    points = ((-.5, 0.0), (-.25, -.12), (0.0, -.15), (.25, -.12), (.5, 0.0))
    base = compose_ocular_basis()
    rotated = compose_ocular_basis(pose=OcularPose3D(alignment_axis_rotation_deg=45))
    projected, world = couple_lid_curve(points, center=(0, 0, 0), radius=.5, basis=rotated)
    assert projected[0] == points[0] and projected[-1] == points[-1]
    assert len(world) == len(points)
    assert all(all(math.isfinite(v) for v in p) for p in projected)
    assert all(all(math.isfinite(v) for v in p) for p in world)


def test_bilateral_opposite_alignment_keeps_two_independent_children():
    from visual_engine.components.face.eyes import EyePairSpec
    pair = build_eye_pair(EyePairSpec(
        left_parameters=EyeParameters(alignment_axis_rotation_deg=35, iris_offset_y=.02),
        right_parameters=EyeParameters(alignment_axis_rotation_deg=-35, iris_offset_y=-.02),
        policy=EyePairPolicy(max_alignment_axis_rotation_delta_deg=90.0),
    ))
    assert pair.left.spherical_assembly is not None
    assert pair.right.spherical_assembly is not None
    assert pair.left.spherical_assembly.alignment_coupling.sign == "alignment_positive"
    assert pair.right.spherical_assembly.alignment_coupling.sign == "alignment_negative"
