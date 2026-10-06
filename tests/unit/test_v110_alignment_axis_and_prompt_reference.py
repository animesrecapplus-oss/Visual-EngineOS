from __future__ import annotations

import math

import pytest
from PIL import Image

from visual_engine.components.common.meta import Component, Parameter
from visual_engine.components.common.visual_contract import LocalTransform
from visual_engine.components.face.eyes.gaze.semantics import prompt_intent_names, resolve_prompt_intent
from visual_engine.components.face.eyes.geometry.orientation import ocular_local_to_world, project_alignment_axis, project_ellipse_axes
from visual_engine.components.face.eyes.reference import (
    ReferenceEngineAlignment, ReferenceFamily, ReferenceSample, ReferenceCurve,
    TraceRegion, digitize_approved_eye, overlay_metrics, render_reference_engine_overlay, trace_component_candidates,
    inspect_image_metadata, preserve_reference_file,
)
from visual_engine.geometry import EyePairPolicy, EyePairSpec, EyeParameters, Gaze, build_eye_geometry, build_eye_pair
from visual_engine.render import render_eye_svg
from visual_engine.components.face.eyes.generator import EYE_GEOMETRY_GENERATOR_VERSION
from visual_engine.runtime import RuntimeGraph, resolve_geometry_transform
from visual_engine.components.face.eyes.geometry.runtime_transform import resolve_alignment_axis_rotation


def test_alignment_axis_projection_is_identity_at_zero_and_even_in_sign():
    p=(.7,-.4)
    assert project_alignment_axis(p,0)==pytest.approx(p)
    assert project_alignment_axis(p,30)[1] == pytest.approx(project_alignment_axis(p,-30)[1])


def test_alignment_axis_keeps_face_canthus_anchors_but_allows_lid_surface_follow():
    base=build_eye_geometry(EyeParameters(width=2,height=1,alignment_axis_rotation_deg=0))
    tilted=build_eye_geometry(EyeParameters(width=2,height=1,alignment_axis_rotation_deg=60))
    assert tilted.inner_canthus == pytest.approx(base.inner_canthus)
    assert tilted.outer_canthus == pytest.approx(base.outer_canthus)
    assert tilted.spherical_assembly is not None
    assert tilted.spherical_assembly.basis.vertical_axis != pytest.approx((0.0, 1.0, 0.0))
    assert any(abs(a-b) > 1e-8 for pa, pb in zip(tilted.upper_lid_points, base.upper_lid_points) for a,b in zip(pa,pb))


def test_roll_and_alignment_axis_are_independent_composable_transforms():
    point=(.4,.2)
    expected=ocular_local_to_world(point,roll_deg=45,alignment_axis_rotation_deg=30)
    assert expected == pytest.approx((.4*math.cos(math.radians(45))-.2*math.cos(math.radians(30))*math.sin(math.radians(45)), .4*math.sin(math.radians(45))+.2*math.cos(math.radians(30))*math.cos(math.radians(45))))


def test_projected_internal_ellipses_inherit_roll_and_depth_foreshortening():
    g=build_eye_geometry(EyeParameters(rotation_deg=45,alignment_axis_rotation_deg=60))
    assert g.iris_ry < g.iris_rx
    assert g.iris_rotation_deg == pytest.approx(45)
    assert g.pupil_rotation_degs[0] == pytest.approx(45)
    assert g.reflection_ry < g.reflection_rx
    assert g.reflection_rotation_deg == pytest.approx(45)


def test_alignment_axis_does_not_rotate_pair_centerline():
    pair=build_eye_pair(EyePairSpec(base_parameters=EyeParameters(alignment_axis_rotation_deg=60)),strength=0)
    assert pair.left.center_y == pytest.approx(pair.right.center_y)
    assert pair.left.alignment_axis_rotation_deg == pytest.approx(60)
    assert pair.right.alignment_axis_rotation_deg == pytest.approx(60)


def test_pair_alignment_axis_asymmetry_is_explicitly_constrained():
    with pytest.raises(ValueError, match="alignment-axis rotation asymmetry"):
        build_eye_pair(EyePairSpec(
            base_parameters=EyeParameters(),
            left_parameters=EyeParameters(alignment_axis_rotation_deg=20),
            right_parameters=EyeParameters(alignment_axis_rotation_deg=-20),
        ))


def test_parent_alignment_axis_rotation_accumulates_separately_from_2d_matrix():
    root=Component("face","HumanFace",parameters={"alignment_axis_rotation_deg": Parameter("alignment_axis_rotation_deg",20)})
    eye=Component("eye","Eye",parameters={"alignment_axis_rotation_deg": Parameter("alignment_axis_rotation_deg",15)})
    root.add_child(eye)
    graph=RuntimeGraph.from_component(root)
    assert resolve_alignment_axis_rotation(graph,"eye") == pytest.approx(35)
    resolved=resolve_geometry_transform(graph,"eye")
    assert resolved.local_to_world[0] == pytest.approx((1,0,0))
    assert resolved.local_to_world[1] == pytest.approx((0,1,0))
    assert resolved.local_to_world[2] == pytest.approx((0,0,1))


def test_prompt_vocabulary_keeps_behind_intent_depth_explicit():
    intent=resolve_prompt_intent("look behind with right eye")
    assert intent.name == "look_behind_right_eye"
    assert intent.eye == "right"
    assert intent.yaw_deg == 180
    assert intent.requires_depth_projection is True
    assert "look_behind_right_eye" in prompt_intent_names()


def test_prompt_unknown_does_not_get_guessed():
    with pytest.raises(ValueError):
        resolve_prompt_intent("look somewhere mysterious")


def test_source_metadata_and_immutable_preservation(tmp_path):
    source=tmp_path/"ref.jpg"; Image.new("RGB",(32,24),(255,255,255)).save(source)
    meta=inspect_image_metadata(source)
    assert meta["format"] == "JPEG" and meta["orientation"] == "normal"
    dest=tmp_path/"stored.jpg"
    record=preserve_reference_file(source,dest)
    assert record.actual_sha256 == meta["sha256"]
    source.write_bytes(b"not-a-jpeg")
    with pytest.raises(ValueError):
        preserve_reference_file(source,dest)


def test_trace_candidates_are_review_only_and_approved_gate_is_hard(tmp_path):
    source=tmp_path/"eye.png"; im=Image.new("RGB",(80,50),(255,255,255)); px=im.load()
    for x in range(10,70):
        y=20-abs(x-40)//8
        for yy in range(y-1,y+2): px[x,yy]=(0,0,0)
        y=30+abs(x-40)//8
        for yy in range(y-1,y+2): px[x,yy]=(0,0,0)
    im.save(source)
    region=TraceRegion(0,0,80,50,"sample")
    candidates=trace_component_candidates(source,region)
    assert candidates["status"] == "manual_component_selection_required"
    assert candidates["candidate_count"] >= 2
    with pytest.raises(ValueError, match="explicitly approved"):
        digitize_approved_eye(source,region,family=ReferenceFamily.ANIME_STYLIZED,upper_candidate_id="ink_001",lower_candidate_id="ink_002",medial_terminal_px=(10,20),lateral_terminal_px=(70,30))


def test_overlay_uses_explicit_mapping_and_resamples_without_fitting_engine():
    sample=ReferenceSample("s",ReferenceFamily.ANIME_STYLIZED,
        upper=ReferenceCurve("upper",((0,0),(2,-1),(4,0),(6,1))),
        lower=ReferenceCurve("lower",((0,0),(2,1),(4,0),(6,-1))),
        medial_terminal_px=(0,0),lateral_terminal_px=(6,1))
    engine=build_eye_geometry(EyeParameters(width=1.0,height=.55))
    alignment=ReferenceEngineAlignment((0,0),(6,1),engine.inner_canthus,engine.outer_canthus,.5,engine.visible_height)
    metrics=overlay_metrics(sample,engine,alignment)
    assert metrics["sample_id"] == "s"
    assert metrics["upper_error"]["mean_error"] >= 0


def test_overlay_forward_inverse_mapping_is_stable():
    alignment=ReferenceEngineAlignment((10,20),(70,20),(0,0),(2,0),10,2)
    for point in ((10,20),(40,25),(70,15)):
        assert alignment.inverse_map(alignment.map(point)) == pytest.approx(point)


def test_overlay_renderer_writes_same_source_canvas_without_mutating_geometry(tmp_path):
    source=tmp_path/"source.png"; Image.new("RGB",(100,80),(255,255,255)).save(source)
    sample=ReferenceSample("s",ReferenceFamily.ANIME_STYLIZED,
        upper=ReferenceCurve("upper",((10,30),(30,20),(50,20),(70,30))),
        lower=ReferenceCurve("lower",((10,30),(30,40),(50,40),(70,30))),
        medial_terminal_px=(10,30),lateral_terminal_px=(70,30))
    engine=build_eye_geometry(EyeParameters(width=2,height=1))
    alignment=ReferenceEngineAlignment((10,30),(70,30),engine.inner_canthus,engine.outer_canthus,.5,engine.visible_height)
    out=tmp_path/"overlay.png"
    result=render_reference_engine_overlay(str(source),sample,engine,alignment,str(out))
    assert out.exists() and result["width_px"] == 100 and result["height_px"] == 80


def test_eye_geometry_generator_version_changes_for_new_projection_contract():
    assert EYE_GEOMETRY_GENERATOR_VERSION == "10"
