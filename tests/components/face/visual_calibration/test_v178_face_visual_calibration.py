from __future__ import annotations

import hashlib
import math

import pytest

from visual_engine.components.common.meta import Anchor, Parameter
from visual_engine.components.common.visual_contract import ContourContract, VisualContract
from visual_engine.components.face.generators import FaceGeometryInputs, _head_geometry, generate_nose_geometry
from visual_engine.components.face.hair import generate_hair_geometry
from visual_engine.entities import build_human_face
from visual_engine.math import Vec2
from visual_engine.render.geometry_svg import GeometrySvgTheme
from visual_engine.runtime import ProductionRenderSession
from visual_engine.scene.composition import Camera, Placement


def _render(root, theme=None):
    with ProductionRenderSession(root) as session:
        return session.render_face(
            "face-01",
            placement=Placement("face-01", Vec2(450, 450), scale=650),
            camera=Camera(),
            theme=theme,
        )


def test_v178_default_eye_ear_centers_share_aesthetic_alignment():
    root = build_human_face("face-01")
    left_eye, right_eye = root.find("left_eye"), root.find("right_eye")
    left_ear, right_ear = root.find("left_ear"), root.find("right_ear")
    assert left_eye and right_eye and left_ear and right_ear
    assert left_eye.anchors["center"].y == pytest.approx(left_ear.anchors["center"].y)
    assert right_eye.anchors["center"].y == pytest.approx(right_ear.anchors["center"].y)


def test_v178_nose_bridge_stays_below_eye_center_and_mouth_has_clear_gap():
    root = build_human_face("face-01")
    nose, mouth = root.find("nose"), root.find("mouth")
    assert nose and mouth
    nose_geometry = generate_nose_geometry(nose)
    nose_top = nose_geometry.bounds.min_y + nose.anchors["center"].y
    nose_tip = nose_geometry.anchors["tip"][1] + nose.anchors["center"].y
    mouth_top = mouth.anchors["center"].y - 0.5 * float(mouth.parameters["height"].value)
    assert nose_top >= 0.0
    assert nose_tip < mouth_top
    assert mouth_top - nose_tip >= 0.08


def test_v178_hair_covers_head_top_without_flat_cap_and_has_detail_paths():
    root = build_human_face("face-01")
    hair, head = root.find("hair"), _head_geometry(root, FaceGeometryInputs())
    assert hair is not None
    hair_geometry = generate_hair_geometry(hair)
    assert hair_geometry.bounds.min_y < head.bounds.min_y
    assert len(hair_geometry.paths) >= 2
    assert any(surface.name.startswith("hair_detail:") for surface in hair_geometry.surfaces)
    assert sum(1 for command, _ in hair_geometry.paths[0].commands if command == "C") >= 6


def test_v178_hair_detail_density_is_deterministic_and_bounded():
    root = build_human_face("face-01")
    hair = root.find("hair")
    assert hair is not None
    hair.set_parameter(Parameter("strand_density", 0.0, 0.0, 1.0))
    sparse = generate_hair_geometry(hair)
    hair.set_parameter(Parameter("strand_density", 1.0, 0.0, 1.0))
    dense = generate_hair_geometry(hair)
    assert len(sparse.paths) == 1
    assert len(dense.paths) == 5
    assert sparse.paths[0] == dense.paths[0]


def test_v178_hair_rejects_non_finite_or_out_of_range_detail_density():
    root = build_human_face("face-01")
    hair = root.find("hair")
    assert hair is not None
    for value in (math.nan, math.inf, -0.1, 1.1):
        with pytest.raises(ValueError):
            bad = type(hair)(hair.id, hair.kind, parameters=dict(hair.parameters), anchors=dict(hair.anchors))
            bad.parameters["strand_density"] = Parameter("strand_density", value, 0.0, 1.0)
            generate_hair_geometry(bad)


def test_v178_shape_color_and_granularity_variants_change_real_render():
    baseline = build_human_face("face-01")
    base = _render(baseline)

    shape = build_human_face("face-01")
    for eye_id in ("left_eye", "right_eye"):
        eye = shape.find(eye_id)
        assert eye is not None
        eye.set_parameter(Parameter("width", 0.34, 0.05, 1.0))
        eye.set_parameter(Parameter("height", 0.18, 0.03, 0.8))
        eye.set_parameter(Parameter("iris_ratio", 0.62, 0.1, 0.9))
    shape_result = _render(shape, GeometrySvgTheme(iris="#3f8f6b"))

    color = build_human_face("face-01")
    color.visual = VisualContract(fill_color="#c7835a", contour=ContourContract(color="#4b251d", width=2.5))
    hair = color.find("hair")
    assert hair is not None
    hair.visual = VisualContract(fill_color="#5a1637", contour=ContourContract(color="#35131b", width=2.0))
    color_result = _render(color, GeometrySvgTheme(iris="#8a5a2b"))

    hashes = {hashlib.sha256(result.svg.encode()).hexdigest() for result in (base, shape_result, color_result)}
    assert len(hashes) == 3
