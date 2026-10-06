from dataclasses import replace

import pytest

from visual_engine.geometry import EyeParameters, CanthusTerminalSpec, build_eye_geometry
from visual_engine.components.face.eyes.morphology.orthogonality import (
    ALLOWED_CHANNELS, assess_parameter_orthogonality,
)
from visual_engine.components.face.eyes.visibility import EyeVisibilitySpec
from visual_engine.render import render_eye_svg


def _build(p):
    return build_eye_geometry(__import__("dataclasses").replace(p, canthus_inner_terminal=CanthusTerminalSpec("bridge"), canthus_outer_terminal=CanthusTerminalSpec("bridge")))


@pytest.mark.parametrize("name", tuple(ALLOWED_CHANNELS))
def test_morphology_parameter_has_only_declared_output_scope(name):
    base = EyeParameters(
        width=2.0, height=1.0, opening=.82, iris_offset_x=.0, iris_offset_y=.0,
        pupil_offset_x=.0, pupil_offset_y=0.0, contour_wave_amplitude=.04,
        contour_wave_frequency=1.7, epicanthic_fold=.65,
    )
    values = {
        "width": 2.12, "height": 1.08, "opening": .71, "upper_curve": 1.08,
        "lower_curve": 1.04, "asymmetry": .25, "rotation_deg": 11.0,
        "contour_irregularity": .5, "contour_wave_amplitude": .07,
        "contour_wave_frequency": 2.4, "canthus_inner_roundness": .14,
        "canthus_outer_roundness": .12, "epicanthic_fold": .25,
    }
    changed = replace(base, **{name: values[name]})
    report = assess_parameter_orthogonality(name, base, changed, _build)
    assert report.valid, report
    assert report.changed_channels, f"{name} produced no measurable geometry change"


def test_inner_canthus_change_cannot_contaminate_outer_or_internal_assembly():
    a = build_eye_geometry(EyeParameters(width=2, height=1, canthus_inner_roundness=.01))
    b = build_eye_geometry(EyeParameters(width=2, height=1, canthus_inner_roundness=.18))
    assert a.outer_canthus == b.outer_canthus
    assert a.outer_canthus_bridge == b.outer_canthus_bridge
    assert a.iris_center == b.iris_center and a.iris_rx == b.iris_rx
    assert a.pupil_centers == b.pupil_centers and a.pupil_radii == b.pupil_radii


def test_epicanthic_fold_is_inner_canthus_only():
    a = build_eye_geometry(EyeParameters(width=2, height=1, epicanthic_fold=0.0))
    b = build_eye_geometry(EyeParameters(width=2, height=1, epicanthic_fold=.9))
    assert a.contour_points == b.contour_points
    assert a.inner_canthus == b.inner_canthus and a.outer_canthus == b.outer_canthus
    assert a.iris_center == b.iris_center and a.pupil_centers == b.pupil_centers
    assert a.epicanthic_fold_points != b.epicanthic_fold_points


def test_visibility_is_hierarchical_and_sibling_specific():
    v = EyeVisibilitySpec({"pupil": False, "highlight": True})
    assert not v.is_visible("pupil")
    assert not v.is_visible("pupil_glow") and not v.is_visible("pupil_smoke")
    assert v.is_visible("highlight") and v.is_visible("reflection") and v.is_visible("reflection_marks")
    assert v.is_visible("iris") and v.is_visible("lashes") and v.is_visible("eyebrow")


def test_render_without_pupils_keeps_explicit_highlight():
    from visual_engine.components.face.eyes.highlights.spec import ReflectionMark
    app = __import__("visual_engine.geometry.eye", fromlist=["EyeAppearance"]).EyeAppearance(
        visibility=EyeVisibilitySpec({"pupil": False, "highlight": True}),
        reflection_marks=(ReflectionMark(x=.1, y=-.1),),
    )
    svg = render_eye_svg(build_eye_geometry(), appearance=app)
    assert 'role="pupil"' not in svg
    assert 'opacity="0.900000"' in svg


def test_contour_variation_does_not_move_internal_assembly_even_with_nominal_offsets():
    base = EyeParameters(width=2, height=1, iris_offset_x=.08, iris_offset_y=.04, pupil_offset_x=.03, contour_wave_amplitude=.0)
    varied = replace(base, contour_wave_amplitude=.08, contour_irregularity=.8)
    a, b = build_eye_geometry(base), build_eye_geometry(varied)
    assert a.iris_center == b.iris_center
    assert a.pupil_centers == b.pupil_centers


def test_visibility_parent_false_disables_descendants_but_not_siblings():
    v = EyeVisibilitySpec({"iris": False, "highlight": True})
    assert not v.is_visible("iris") and not v.is_visible("limbal_ring") and not v.is_visible("rings")
    assert v.is_visible("highlight") and v.is_visible("reflection")


def test_visibility_toggle_is_presentation_only_and_does_not_change_geometry_cache_inputs():
    from visual_engine.components.face.eyes.generator import EyeGeometryInputs, _eye_cache_inputs
    base = EyeGeometryInputs()
    hidden = EyeGeometryInputs(appearance=__import__("visual_engine.geometry.eye", fromlist=["EyeAppearance"]).EyeAppearance(visibility=EyeVisibilitySpec({"pupil": False})))
    assert _eye_cache_inputs(base) == _eye_cache_inputs(hidden)
