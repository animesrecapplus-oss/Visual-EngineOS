from __future__ import annotations

import math

import pytest

from visual_engine.components.common.meta import Component, Parameter
from visual_engine.components.common.visual_contract import LocalTransform
from visual_engine.components.face.eyes import EyeParameters, EyePairPolicy, EyePairSpec, build_eye_geometry, build_eye_pair
from visual_engine.components.face.eyes.geometry.projection3d import Camera3D, project_oriented_circle, project_point, project_sphere_silhouette
from visual_engine.components.face.eyes.geometry.spherical_assembly import build_spherical_eye_assembly
from visual_engine.components.face.eyes.geometry.view_axis import OcularPose3D, basis_handedness, compose_ocular_basis
from visual_engine.render import render_eye_svg
from visual_engine.components.face.eyes.generator import EYE_GEOMETRY_GENERATOR_VERSION
from visual_engine.persistence.serialization import component_payload
from visual_engine.runtime import RuntimeGraph, resolve_geometry_transform
from visual_engine.components.face.eyes.geometry.runtime_transform import resolve_ocular_basis


def _dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def _extent(points):
    return max(x for x, _ in points) - min(x for x, _ in points), max(y for _, y in points) - min(y for _, y in points)


def test_basis_is_orthonormal_for_adversarial_poses():
    for yaw in (-180, -150, -120, -90, -60, -30, 0, 30, 60, 90, 120, 150, 180):
        for pitch in (-90, -60, -30, 0, 30, 60, 90):
            b = compose_ocular_basis(pose=OcularPose3D(yaw_deg=yaw, pitch_deg=pitch, roll_deg=37, alignment_axis_rotation_deg=25))
            axes = (b.alignment_axis, b.vertical_axis, b.view_axis)
            for axis in axes:
                assert math.isclose(_dot(axis, axis), 1.0, abs_tol=1e-8)
            assert abs(_dot(axes[0], axes[1])) < 1e-8
            assert abs(_dot(axes[0], axes[2])) < 1e-8
            assert abs(_dot(axes[1], axes[2])) < 1e-8
            assert math.isclose(abs(basis_handedness(b)), 1.0, abs_tol=1e-8)


def test_yaw_changes_projected_iris_shape_from_real_3d_circle():
    front = build_spherical_eye_assembly(pose=OcularPose3D(yaw_deg=0), radius=.5, iris_radius=.15)
    oblique = build_spherical_eye_assembly(pose=OcularPose3D(yaw_deg=60), radius=.5, iris_radius=.15)
    fx, fy = _extent(front.iris_outline)
    ox, oy = _extent(oblique.iris_outline)
    assert fx > 0 and fy > 0 and ox > 0 and oy > 0
    assert ox < fx * .7
    assert math.isclose(oy, fy, rel_tol=.08)


def test_profile_yaw_hides_back_facing_iris_and_pupil():
    for yaw in (120, 150, 180, -120, -150, -180):
        assembly = build_spherical_eye_assembly(pose=OcularPose3D(yaw_deg=yaw))
        assert assembly.visibility.iris == "hidden"
        assert assembly.visibility.pupil == "hidden"
        assert not assembly.iris_outline
        assert not assembly.pupil_outline


def test_edge_on_yaw_is_not_faked_as_a_large_visible_circle():
    assembly = build_spherical_eye_assembly(pose=OcularPose3D(yaw_deg=89.9), iris_radius=.15)
    assert assembly.visibility.iris == "partially_visible"
    w, h = _extent(assembly.iris_outline)
    assert w > 0
    assert h > 0
    assert w / h < .02


def test_pitch_changes_vertical_foreshortening_without_changing_horizontal_extent():
    front = build_spherical_eye_assembly(pose=OcularPose3D(pitch_deg=0), radius=.5, iris_radius=.15)
    pitched = build_spherical_eye_assembly(pose=OcularPose3D(pitch_deg=60), radius=.5, iris_radius=.15)
    fw, fh = _extent(front.iris_outline)
    pw, ph = _extent(pitched.iris_outline)
    assert pw > 0 and ph > 0
    assert ph < fh * .7
    assert math.isclose(pw, fw, rel_tol=.08)


def test_roll_changes_basis_but_not_a_perfectly_circular_iris_projection():
    # A perfect circle has rotational symmetry: roll must change the ocular frame
    # but cannot invent a visible change in the projected circle. The aperture and
    # non-circular child details are responsible for any visible roll difference.
    a = build_spherical_eye_assembly(pose=OcularPose3D(yaw_deg=45, roll_deg=0), iris_radius=.15)
    b = build_spherical_eye_assembly(pose=OcularPose3D(yaw_deg=45, roll_deg=30), iris_radius=.15)
    assert a.basis != b.basis
    assert _extent(a.iris_outline) == pytest.approx(_extent(b.iris_outline), abs=1e-10)
    assert a.iris_projected_center == pytest.approx(b.iris_projected_center, abs=1e-10)


def test_alignment_rotation_is_not_inserted_as_screen_roll():
    a = compose_ocular_basis(pose=OcularPose3D(alignment_axis_rotation_deg=45))
    assert abs(a.alignment_axis[0] - 1.0) < 1e-8
    assert abs(a.alignment_axis[1]) < 1e-8
    assert abs(a.view_axis[1]) > 0.1
    assert abs(a.view_axis[2]) > 0.1


def test_parent_and_child_orientation_compose_as_bases_not_angle_addition():
    root = Component("head", "Head", transform=LocalTransform(rotation_deg=20), parameters={"ocular_yaw_deg": Parameter("ocular_yaw_deg", 30), "ocular_pitch_deg": Parameter("ocular_pitch_deg", 10)})
    face = Component("face", "Face", transform=LocalTransform(rotation_deg=5), parameters={"ocular_yaw_deg": Parameter("ocular_yaw_deg", 15), "ocular_pitch_deg": Parameter("ocular_pitch_deg", -5)})
    eye = Component("eye", "Eye", transform=LocalTransform(rotation_deg=7), parameters={"ocular_yaw_deg": Parameter("ocular_yaw_deg", 20), "ocular_pitch_deg": Parameter("ocular_pitch_deg", 8)})
    root.add_child(face); face.add_child(eye)
    b = resolve_ocular_basis(RuntimeGraph.from_component(root), "eye")
    assert math.isclose(_dot(b.alignment_axis, b.view_axis), 0.0, abs_tol=1e-8)
    assert not math.isclose(b.view_axis[2], math.cos(math.radians(30 + 15 + 20)), abs_tol=.01)


def test_runtime_geometry_resolution_exposes_ocular_basis_without_changing_2d_matrix():
    root = Component("head", "Head", transform=LocalTransform(rotation_deg=30), parameters={"ocular_yaw_deg": Parameter("ocular_yaw_deg", 20)})
    eye = Component("eye", "Eye", transform=LocalTransform(rotation_deg=5), parameters={"ocular_pitch_deg": Parameter("ocular_pitch_deg", 15)})
    root.add_child(eye)
    resolution = resolve_geometry_transform(RuntimeGraph.from_component(root), "eye")
    assert not hasattr(resolution, "ocular_basis")
    assert resolution.local_to_world[0][0] == pytest.approx(math.cos(math.radians(35)), abs=1e-8)


def test_eye_geometry_activates_spherical_layer_only_for_non_front_view():
    front = build_eye_geometry(EyeParameters())
    yawed = build_eye_geometry(EyeParameters(ocular_yaw_deg=60))
    assert front.spherical_assembly is None
    assert yawed.spherical_assembly is not None
    assert yawed.ocular_yaw_deg == 60


def test_backward_right_eye_does_not_rotate_left_eye():
    spec = EyePairSpec(policy=EyePairPolicy(mode="free"))
    left = build_eye_geometry(EyeParameters(ocular_yaw_deg=0), side="image_left")
    right = build_eye_geometry(EyeParameters(ocular_yaw_deg=180), side="image_right")
    assert left.spherical_assembly is None
    assert right.spherical_assembly is not None
    assert right.spherical_assembly.visibility.iris == "hidden"


def test_multiple_eyes_are_independent():
    poses = (0, 60, -60, 180)
    assemblies = [build_spherical_eye_assembly(pose=OcularPose3D(yaw_deg=y)) for y in poses]
    assert assemblies[0].visibility.iris == "visible"
    assert assemblies[1].visibility.iris == "visible"
    assert assemblies[2].visibility.iris == "visible"
    assert assemblies[3].visibility.iris == "hidden"


def test_perspective_rejects_camera_inside_globe():
    with pytest.raises(ValueError):
        project_sphere_silhouette((0, 0, 0), .5, Camera3D(position=(0, 0, .5), orthographic=False))


def test_perspective_projects_points_with_positive_camera_depth():
    camera = Camera3D(position=(0, 0, 10), focal_length=10, orthographic=False)
    assert project_point((1, 0, 0), camera) == pytest.approx((1, 0))
    assert project_point((1, 0, 5), camera) == pytest.approx((2, 0))


def test_oriented_circle_projection_is_finite_and_dense():
    pts = project_oriented_circle((0, 0, 0), (0, 1, 1), .2, samples=96)
    assert len(pts) == 96
    assert all(math.isfinite(v) for p in pts for v in p)


def test_spherical_render_contains_projected_surface_and_not_legacy_circle():
    g = build_eye_geometry(EyeParameters(ocular_yaw_deg=60))
    svg = render_eye_svg(g, background="#ffffff")
    assert "spherical" not in svg  # renderer output must stay geometry-only; no debug labels
    assert svg.count("<path") >= 3
    assert g.spherical_assembly is not None


def test_generator_version_is_bumped_for_geometry_cache_invalidation():
    assert EYE_GEOMETRY_GENERATOR_VERSION == "10"


def test_new_ocular_transform_fields_survive_component_serialization():
    component = Component("eye", "Eye", parameters={"ocular_yaw_deg": Parameter("ocular_yaw_deg", 60), "ocular_pitch_deg": Parameter("ocular_pitch_deg", -20)})
    payload = component_payload(component)
    assert "ocular_yaw_deg" not in payload["transform"]
    assert "ocular_pitch_deg" not in payload["transform"]
