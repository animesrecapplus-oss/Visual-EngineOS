from __future__ import annotations

import math

import pytest

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.visual_contract import VisualContract
from visual_engine.components.face.ear import generate_ear_geometry
from visual_engine.components.face.generators import generate_face_geometry
from visual_engine.entities import build_human_face
from visual_engine.runtime import (
    ProductionRenderSession,
    ProductionHeadEarOcclusion,
    resolve_head_ear_occlusion,
    resolve_production_pair_occlusion,
)
from visual_engine.scene.composition import Camera, Placement
from visual_engine.math import Vec2


def _request(session: ProductionRenderSession):
    return session.render_face(
        "face-01", placement=Placement("face-01", Vec2(450, 450), scale=650), camera=Camera()
    )


def test_v159_real_head_ear_overlap_is_resolved_for_both_ears():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
    assert len(result.head_ear_occlusion) == 2
    assert {item.ear_id for item in result.head_ear_occlusion} == {"left_ear", "right_ear"}
    assert all(item.head_id == "face-01" for item in result.head_ear_occlusion)
    assert all(0.0 < item.coverage < 1.0 for item in result.head_ear_occlusion)
    assert all(0.0 < item.visible < 1.0 for item in result.head_ear_occlusion)
    assert all(item.depth_relation.value == "coplanar" for item in result.head_ear_occlusion)


def test_v159_head_ear_visibility_matches_measured_overlap():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
    left, right = result.head_ear_occlusion
    assert left.coverage == pytest.approx(0.1566009294769769)
    assert right.coverage == pytest.approx(0.2189580969228517)
    assert left.visible == pytest.approx(1.0 - left.coverage)
    assert right.visible == pytest.approx(1.0 - right.coverage)


def test_v159_hidden_head_removes_optical_occlusion_but_keeps_geometry():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        visible = _request(session)
        old = root.visual
        root.visual = VisualContract(
            fill_color=old.fill_color, contour=old.contour, material=old.material,
            opacity=old.opacity, visibility=0.0,
        )
        hidden = _request(session)
    assert all(item.coverage > 0.0 for item in hidden.head_ear_occlusion)
    assert all(item.visible == pytest.approx(1.0) for item in hidden.head_ear_occlusion)
    assert [item.coverage for item in hidden.head_ear_occlusion] == pytest.approx(
        [item.coverage for item in visible.head_ear_occlusion]
    )


def test_v159_wrong_kinds_nan_and_non_boolean_coplanar_flag_fail_closed():
    root = build_human_face("face-01")
    ear = root.find("left_ear")
    assert ear is not None
    with pytest.raises(ValueError, match="Ear then HumanFace"):
        resolve_head_ear_occlusion(ear, generate_ear_geometry(ear), 0.0, ear, generate_ear_geometry(ear), 0.0)
    with pytest.raises(ValueError, match="finite"):
        resolve_production_pair_occlusion(
            ear, generate_ear_geometry(ear), math.nan, root, generate_face_geometry(root), 0.0
        )
    with pytest.raises(TypeError, match="coplanar_occludes"):
        resolve_production_pair_occlusion(
            ear, generate_ear_geometry(ear), 0.0, root, generate_face_geometry(root), 0.0,
            coplanar_occludes=1,
        )


def test_v159_pair_rejects_ambiguous_region_owner_geometry():
    root = build_human_face("face-01")
    ear = root.find("left_ear")
    assert ear is not None
    empty = GeometryContract(coordinate_frame="component")
    with pytest.raises(ValueError, match="exactly one area region"):
        resolve_production_pair_occlusion(ear, empty, 0.0, root, generate_face_geometry(root), 0.0)


def test_v159_public_contract_and_previous_generator_remain_compatible():
    root = build_human_face("face-01")
    assert ProductionHeadEarOcclusion.__name__ == "ProductionHeadEarOcclusion"
    with ProductionRenderSession(root) as session:
        previous = session.render_face(
            "face-01", placement=Placement("face-01", Vec2(450, 450), scale=650), camera=Camera(),
            generator="face.human_with_eyes_nose_mouth_ears",
        )
    assert previous.head_ear_occlusion == ()


def test_v159_head_ear_semantics_match_renderer_paint_order():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
    paths = {s.name: int(s.data["path_index"]) for s in result.camera_geometry.surfaces if "path_index" in s.data}
    def path_text(index: int) -> str:
        return " ".join(command + (" " + " ".join(f"{v:.6f}" for v in values) if values else "") for command, values in result.camera_geometry.paths[index].commands)
    assert result.svg.find(path_text(paths["face:left_ear:ear"])) < result.svg.find(path_text(paths["face:face:head:head"]))
    assert result.svg.find(path_text(paths["face:right_ear:ear"])) < result.svg.find(path_text(paths["face:face:head:head"]))
    assert all(item.depth_relation.value == "coplanar" for item in result.head_ear_occlusion)
