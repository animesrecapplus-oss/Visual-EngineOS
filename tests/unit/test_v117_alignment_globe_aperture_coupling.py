from __future__ import annotations

import math
import pytest

from visual_engine.components.face.eyes import EyeParameters, build_eye_geometry
from visual_engine.components.face.eyes.geometry.alignment_coupling import alignment_sign, resolve_alignment_coupling
from visual_engine.components.face.eyes.geometry.orientation import face_local_to_world
from visual_engine.components.face.eyes.geometry.view_axis import OcularPose3D, compose_ocular_basis
from visual_engine.render import render_eye_svg


def _aperture(g):
    return tuple(g.upper_lid_points + tuple(reversed(g.lower_lid_points)))


def test_positive_and_negative_alignment_have_explicit_semantics():
    assert alignment_sign(0) == "alignment_neutral"
    assert alignment_sign(30) == "alignment_positive"
    assert alignment_sign(-30) == "alignment_negative"


def test_alignment_keeps_canthi_face_owned_but_allows_interior_lid_surface_coupling():
    base = build_eye_geometry(EyeParameters(alignment_axis_rotation_deg=0))
    pos = build_eye_geometry(EyeParameters(alignment_axis_rotation_deg=60))
    neg = build_eye_geometry(EyeParameters(alignment_axis_rotation_deg=-60))
    # Semantic face anchors remain fixed; the interior lid samples are allowed to
    # slide over the globe so the visible aperture can change shape.
    assert pos.inner_canthus == pytest.approx(base.inner_canthus)
    assert pos.outer_canthus == pytest.approx(base.outer_canthus)
    assert neg.inner_canthus == pytest.approx(base.inner_canthus)
    assert neg.outer_canthus == pytest.approx(base.outer_canthus)
    assert any(abs(a-b) > 1e-8 for pa, pb in zip(pos.upper_lid_points, base.upper_lid_points) for a, b in zip(pa, pb))
    assert any(abs(a-b) > 1e-8 for pa, pb in zip(neg.upper_lid_points, base.upper_lid_points) for a, b in zip(pa, pb))
    assert pos.spherical_assembly is not None and neg.spherical_assembly is not None
    assert pos.spherical_assembly.basis.vertical_axis != pytest.approx((0.0, 1.0, 0.0))
    assert neg.spherical_assembly.basis.vertical_axis != pytest.approx((0.0, 1.0, 0.0))
    assert pos.spherical_assembly.alignment_coupling.sign == "alignment_positive"
    assert neg.spherical_assembly.alignment_coupling.sign == "alignment_negative"


def test_globe_children_share_alignment_basis_and_pupil_remains_iris_child():
    g = build_eye_geometry(EyeParameters(alignment_axis_rotation_deg=55), appearance=None)
    a = g.spherical_assembly
    assert a is not None and a.iris_attachment is not None
    assert a.pupil_attachments
    # Child points remain on the same globe; the pupil cannot become an independent
    # screen-space object merely because the globe rotated in depth.
    c = a.center
    r = a.radius
    for p in (a.iris_surface_center, a.pupil_surface_center):
        assert math.dist(c, p) == pytest.approx(r, rel=1e-7, abs=1e-8)


def test_roll_remains_a_separate_channel_when_alignment_also_changes():
    a = build_eye_geometry(EyeParameters(rotation_deg=30, alignment_axis_rotation_deg=60))
    b = build_eye_geometry(EyeParameters(rotation_deg=30, alignment_axis_rotation_deg=0))
    assert a.rotation_deg == b.rotation_deg == 30
    assert a.alignment_axis_rotation_deg == 60
    assert b.alignment_axis_rotation_deg == 0
    assert any(abs(x - y) > 1e-8 for pa, pb in zip(_aperture(a), _aperture(b)) for x, y in zip(pa, pb))


def test_parent_basis_is_inherited_by_globe_but_not_reinterpreted_as_screen_roll():
    parent = compose_ocular_basis(pose=OcularPose3D(alignment_axis_rotation_deg=20))
    report = resolve_alignment_coupling(parent_basis=parent, alignment_deg=15)
    assert report.globe_children_inherit is True
    assert report.face_aperture_unchanged is True
    assert report.sign == "alignment_positive"


def test_alignment_orthogonality_survives_both_signs():
    for deg in (-89, -60, -30, 0, 30, 60, 89):
        b = compose_ocular_basis(pose=OcularPose3D(alignment_axis_rotation_deg=deg))
        dot = lambda x, y: sum(a*b for a,b in zip(x,y))
        assert abs(dot(b.alignment_axis, b.vertical_axis)) < 1e-8
        assert abs(dot(b.alignment_axis, b.view_axis)) < 1e-8
        assert abs(dot(b.vertical_axis, b.view_axis)) < 1e-8


def test_face_local_transform_is_independent_of_alignment_channel():
    # The API intentionally has no alignment argument: alignment belongs to the
    # globe branch, so a face-owned point cannot accidentally consume it.
    p = (.4, -.2)
    assert face_local_to_world(p, roll_deg=25) == pytest.approx((0.4470467672, -0.0122142527))


def test_generator_cache_version_is_invalidated_for_alignment_contract():
    from visual_engine.components.face.eyes.generator import EYE_GEOMETRY_GENERATOR_VERSION
    assert EYE_GEOMETRY_GENERATOR_VERSION == "10"


def test_prompt_vocabulary_exposes_both_alignment_signs():
    from visual_engine.components.face.eyes.gaze.semantics import resolve_prompt_intent
    positive = resolve_prompt_intent("alignment positive")
    negative = resolve_prompt_intent("alignment negative")
    assert positive.alignment_axis_rotation_deg > 0
    assert negative.alignment_axis_rotation_deg < 0
    assert positive.requires_depth_projection is True
    assert negative.requires_depth_projection is True
