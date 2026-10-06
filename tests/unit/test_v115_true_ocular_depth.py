from __future__ import annotations

import math
import pytest

from visual_engine.components.face.eyes import EyeParameters, build_eye_geometry, EyePairPolicy, EyePairSpec, build_eye_pair
from visual_engine.components.face.eyes.geometry.orbital_surface import build_orbital_surface
from visual_engine.components.face.eyes.geometry.view_axis import OcularPose3D
from visual_engine.components.face.eyes.geometry.spherical_assembly import build_spherical_eye_assembly


def test_orbital_surface_has_finite_ellipsoid_and_front_intersection():
    surface = build_orbital_surface((0.0, 0.0, 0.0), 0.5)
    assert surface.radius_x > surface.radius_z > 0
    assert surface.front_z(0.0, 0.0) == pytest.approx(surface.front_offset + surface.radius_z)
    assert surface.front_z(surface.radius_x * 1.01, 0.0) is None


def test_depth_contract_declares_explicit_ocular_z_order():
    eye = build_eye_geometry(EyeParameters(ocular_yaw_deg=45))
    depth = eye.spherical_assembly.depth_occlusion
    assert depth is not None
    assert depth.z_order == ("orbit", "sclera", "iris", "pupil", "cornea", "eyelid")


def test_lid_depth_is_stored_for_both_margins():
    eye = build_eye_geometry(EyeParameters(ocular_yaw_deg=60))
    depth = eye.spherical_assembly.depth_occlusion
    assert depth is not None
    assert depth.upper_lid.sample_count == len(eye.upper_lid_points)
    assert depth.lower_lid.sample_count == len(eye.lower_lid_points)
    assert depth.upper_lid.depth_max >= depth.upper_lid.depth_min
    assert depth.lower_lid.depth_max >= depth.lower_lid.depth_min


def test_iris_depth_visibility_is_not_allowed_to_ignore_aperture():
    eye = build_eye_geometry(EyeParameters(ocular_yaw_deg=60))
    assembly = eye.spherical_assembly
    depth = assembly.depth_occlusion
    assert depth is not None
    assert 0.0 <= depth.iris_visibility.visible_fraction <= assembly.iris_aperture_fraction + 1e-9


def test_pupil_depth_children_follow_iris_surface_parent():
    eye = build_eye_geometry(EyeParameters(ocular_yaw_deg=55))
    assembly = eye.spherical_assembly
    assert assembly is not None and assembly.iris_attachment is not None
    assert assembly.pupil_surface_samples
    for child in assembly.pupil_attachments:
        assert math.isclose(math.dist(child.center, assembly.center), assembly.radius, abs_tol=1e-8)
        assert child.normal == pytest.approx(assembly.iris_attachment.normal) if child.center == assembly.iris_attachment.center else True


def test_extreme_backward_eye_has_no_front_child_depth():
    eye = build_eye_geometry(EyeParameters(ocular_yaw_deg=180))
    assembly = eye.spherical_assembly
    assert assembly is not None
    assert assembly.visibility.iris == "hidden"
    assert assembly.depth_occlusion.iris_visibility.state == "hidden"


def test_orientations_do_not_break_depth_invariants():
    for yaw in (-150, -120, -90, 90, 120, 150):
        for pitch in (-90, -45, 0, 45, 90):
            eye = build_eye_geometry(EyeParameters(ocular_yaw_deg=yaw, ocular_pitch_deg=pitch, rotation_deg=35, alignment_axis_rotation_deg=20))
            assembly = eye.spherical_assembly
            assert assembly is not None
            depth = assembly.depth_occlusion
            assert depth is not None
            assert depth.near_canthus != depth.far_canthus
            for layer in (depth.upper_lid, depth.lower_lid, depth.iris, *depth.pupils):
                assert layer.depth_min <= layer.depth_max


def test_pair_can_have_one_front_and_one_backward_eye_independently():
    spec = EyePairSpec(policy=EyePairPolicy(mode="free"), left_parameters=EyeParameters(ocular_yaw_deg=0), right_parameters=EyeParameters(ocular_yaw_deg=180))
    pair = build_eye_pair(spec, strength=0.0)
    assert pair.left.spherical_assembly is None or pair.left.spherical_assembly.visibility.iris == "visible"
    assert pair.right.spherical_assembly is not None
    assert pair.right.spherical_assembly.visibility.iris == "hidden"
