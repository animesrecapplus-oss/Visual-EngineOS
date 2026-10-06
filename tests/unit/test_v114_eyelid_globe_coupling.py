from __future__ import annotations

import math

import pytest

from visual_engine.components.face.eyes import EyeParameters, EyeAppearance, Gaze, build_eye_geometry
from visual_engine.components.face.eyes.geometry.eyelid_surface import couple_eyelids_to_globe
from visual_engine.components.face.eyes.geometry.spherical_assembly import build_spherical_eye_assembly
from visual_engine.components.face.eyes.geometry.view_axis import OcularPose3D
from visual_engine.components.face.eyes.pupil.spec import PupilSpec


def _dist(a, b):
    return math.sqrt(sum((x-y)**2 for x, y in zip(a, b)))


def test_pupil_is_attached_to_iris_parent_at_front_and_yaw60():
    for yaw in (0, 30, 60):
        eye = build_eye_geometry(EyeParameters(ocular_yaw_deg=yaw))
        assembly = eye.spherical_assembly or build_spherical_eye_assembly(pose=OcularPose3D(yaw_deg=yaw))
        assert assembly.pupil_attachments
        assert _dist(assembly.pupil_surface_center, assembly.iris_surface_center) < 1e-10
        assert assembly.pupil_attachments[0].normal == pytest.approx(assembly.iris_attachment.normal)


def test_pupil_child_follows_iris_when_gaze_moves():
    base = EyeParameters(ocular_yaw_deg=45)
    centered = build_eye_geometry(base, gaze=Gaze(direction="center", strength=1.0))
    shifted = build_eye_geometry(base, gaze=Gaze(direction="right", strength=0.25))
    assert centered.spherical_assembly and shifted.spherical_assembly
    a0 = centered.spherical_assembly
    a1 = shifted.spherical_assembly
    delta_iris = tuple(b-a for a, b in zip(a0.iris_surface_center, a1.iris_surface_center))
    delta_pupil = tuple(b-a for a, b in zip(a0.pupil_surface_center, a1.pupil_surface_center))
    assert _dist(delta_iris, delta_pupil) < 1e-8


def test_authored_pupil_offset_remains_inside_iris_and_inherits_parent_frame():
    appearance = EyeAppearance(pupils=(PupilSpec(x=.2, y=-.1),))
    eye = build_eye_geometry(EyeParameters(ocular_yaw_deg=55), appearance=appearance)
    a = eye.spherical_assembly
    assert a is not None and a.iris_attachment is not None
    child = a.pupil_attachments[0]
    delta = tuple(b-a0 for a0, b in zip(a.iris_surface_center, child.center))
    assert _dist(delta, (0, 0, 0)) < a.radius
    assert math.isclose(_dist(child.center, (0, 0, 0)), a.radius, rel_tol=0, abs_tol=1e-8)
    assert abs(sum(x*y for x,y in zip(child.normal, child.tangent_x))) < 1e-8
    assert abs(sum(x*y for x,y in zip(child.normal, child.tangent_y))) < 1e-8


def test_multiple_pupil_children_share_the_same_iris_parent():
    appearance = EyeAppearance(pupils=(PupilSpec(x=-.1), PupilSpec(x=.1)))
    eye = build_eye_geometry(EyeParameters(ocular_yaw_deg=40), appearance=appearance)
    a = eye.spherical_assembly
    assert a is not None
    assert len(a.pupil_attachments) == 2
    for child in a.pupil_attachments:
        assert abs(sum(x*y for x,y in zip(child.normal, child.tangent_x))) < 1e-8
        assert abs(sum(x*y for x,y in zip(child.normal, child.tangent_y))) < 1e-8
        assert math.isclose(_dist(child.center, (0, 0, 0)), a.radius, rel_tol=0, abs_tol=1e-8)


def test_aperture_occlusion_is_measured_from_projected_samples():
    eye = build_eye_geometry(EyeParameters(ocular_yaw_deg=60))
    a = eye.spherical_assembly
    assert a is not None
    assert 0.0 <= a.iris_aperture_fraction <= 1.0
    assert a.pupil_aperture_fractions
    assert 0.0 <= a.pupil_aperture_fractions[0] <= 1.0
    assert a.visibility.iris in {"visible", "partially_visible", "hidden"}
    assert a.iris_aperture_fraction < 1.0


def test_eyelid_surface_lift_uses_sphere_then_orbital_shell():
    eye = build_eye_geometry(EyeParameters(ocular_yaw_deg=30))
    a = eye.spherical_assembly
    assert a is not None
    coupling = a.eyelid_coupling
    assert coupling is not None
    assert len(coupling.upper.points) == len(eye.upper_lid_points)
    assert len(coupling.lower.points) == len(eye.lower_lid_points)
    assert coupling.near_canthus in {"inner", "outer"}
    assert coupling.far_canthus in {"inner", "outer"}
    assert coupling.near_canthus != coupling.far_canthus


def test_lid_coupling_does_not_mutate_2d_aperture():
    eye = build_eye_geometry(EyeParameters(ocular_yaw_deg=45))
    a = eye.spherical_assembly
    assert a is not None
    coupling = a.eyelid_coupling
    assert coupling is not None
    # Coupling stores world 3D coordinates; SVG projects world Y with a sign flip.
    for p2, p3 in zip(eye.upper_lid_points, coupling.upper.points):
        assert p2[0] == pytest.approx(p3[0])
        assert p2[1] == pytest.approx(-p3[1])


def test_closed_eye_has_no_visible_internal_surface():
    eye = build_eye_geometry(EyeParameters(ocular_yaw_deg=60), state="closed")
    assert eye.opening == 0.0
    assert eye.spherical_assembly is not None
    # Renderer-level opening gate remains the final blink authority.
    assert eye.spherical_assembly.iris_aperture_fraction == pytest.approx(0.0)


def test_extreme_yaw_and_pitch_keep_child_parent_invariants_or_hide_them():
    for yaw in (-150, -120, -90, 90, 120, 150, 180):
        for pitch in (-90, -60, 60, 90):
            eye = build_eye_geometry(EyeParameters(ocular_yaw_deg=yaw, ocular_pitch_deg=pitch))
            a = eye.spherical_assembly
            assert a is not None
            if a.visibility.iris == "hidden":
                assert not a.iris_outline and not a.pupil_outlines
            else:
                assert a.iris_attachment is not None
                for child in a.pupil_attachments:
                    assert child.normal == pytest.approx(a.iris_attachment.normal)


def test_caruncle_and_epicanthus_are_lifted_as_separate_surface_children():
    eye = build_eye_geometry(EyeParameters(ocular_yaw_deg=25, epicanthic_fold=.7))
    a = eye.spherical_assembly
    assert a is not None
    coupling = a.eyelid_coupling
    assert coupling is not None
    assert coupling.caruncle is not None
    assert coupling.epicanthus is not None
    assert coupling.caruncle.surface_kind in {"globe", "orbital_shell", "globe+orbital_shell"}
    assert coupling.epicanthus.surface_kind in {"globe", "orbital_shell", "globe+orbital_shell"}
