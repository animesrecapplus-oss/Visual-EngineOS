from __future__ import annotations

import hashlib

from visual_engine.components.face.eyes.generator import EYE_GEOMETRY_GENERATOR_VERSION, generate_eye_geometry
from visual_engine.components.common.meta import Component
from visual_engine.entities import build_eye, build_human_face
from visual_engine.math import Vec2
from visual_engine.runtime import ProductionRenderSession
from visual_engine.scene.composition import Camera, Placement


def test_tst_feb_001_human_face_default_eye_generation_preserves_bilateral_identity() -> None:
    root = build_human_face("face-01")
    left = generate_eye_geometry(root.find("left_eye"))
    right = generate_eye_geometry(root.find("right_eye"))

    assert left.anchors["inner_canthus"][0] > left.anchors["outer_canthus"][0]
    assert right.anchors["inner_canthus"][0] < right.anchors["outer_canthus"][0]


def test_tst_feb_002_standalone_eye_keeps_single_side_frame() -> None:
    left_named = build_eye("left_eye", x=-0.22)
    right_named = build_eye("right_eye", x=0.22)

    left = generate_eye_geometry(left_named)
    right = generate_eye_geometry(right_named)

    assert left.anchors["inner_canthus"][0] < left.anchors["outer_canthus"][0]
    assert right.anchors["inner_canthus"][0] < right.anchors["outer_canthus"][0]


def test_adv_feb_001_unrelated_parent_eye_id_does_not_infer_side_from_coordinate() -> None:
    parent = Component("face", "HumanFace")
    child = build_eye("eye_alias", x=-0.22)
    parent.add_child(child)

    geometry = generate_eye_geometry(child)

    assert geometry.anchors["inner_canthus"][0] < geometry.anchors["outer_canthus"][0]


def test_tst_feb_003_production_human_face_propagates_bilateral_identity() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = session.render_face(
            "face-01",
            placement=Placement("face-01", Vec2(450.0, 450.0), scale=650.0),
            camera=Camera(),
            generator="face.human_with_eyes_nose_mouth_ears_hair",
        )

    anchors = result.geometry.geometry.anchors
    assert anchors["face:face:eyes:left_eye:inner_canthus"][0] > anchors["face:face:eyes:left_eye:outer_canthus"][0]
    assert anchors["face:face:eyes:right_eye:inner_canthus"][0] < anchors["face:face:eyes:right_eye:outer_canthus"][0]


def test_tst_feb_004_production_render_is_deterministic_for_identical_request() -> None:
    root = build_human_face("face-01")
    outputs = []
    for _ in range(2):
        with ProductionRenderSession(root) as session:
            result = session.render_face(
                "face-01",
                placement=Placement("face-01", Vec2(450.0, 450.0), scale=650.0),
                camera=Camera(),
                generator="face.human_with_eyes_nose_mouth_ears_hair",
            )
        outputs.append(hashlib.sha256(result.svg.encode()).hexdigest())
    assert outputs[0] == outputs[1]


def test_tst_feb_005_generator_version_is_bumped_for_changed_eye_geometry_defaults() -> None:
    assert EYE_GEOMETRY_GENERATOR_VERSION == "10"
