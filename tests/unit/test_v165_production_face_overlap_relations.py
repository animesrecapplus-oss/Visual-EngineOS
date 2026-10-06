from __future__ import annotations

import math

import pytest

from visual_engine.components.common.visual_contract import VisualContract
from visual_engine.entities import build_human_face
from visual_engine.runtime import ProductionRenderSession, resolve_production_face_overlap_relations
from visual_engine.runtime.production_owner_geometry import extract_production_owner_geometry
from visual_engine.scene.composition import Camera, Placement
from visual_engine.math import Vec2

GENERATORS = (
    "face.human_with_eyes_nose",
    "face.human_with_eyes_nose_mouth",
    "face.human_with_eyes_nose_mouth_ears",
    "face.human_with_eyes_nose_mouth_ears_hair",
)


def _render(session: ProductionRenderSession, generator: str):
    return session.render_face(
        "face-01", placement=Placement("face-01", Vec2(450, 450), scale=650),
        camera=Camera(), generator=generator,
    )


@pytest.mark.parametrize("generator", GENERATORS)
def test_v165_direct_relation_equals_session_result(generator: str) -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _render(session, generator)
        direct = resolve_production_face_overlap_relations(
            root, result.camera_geometry, generator, owner_geometry=extract_production_owner_geometry
        )
    assert direct == result.visibility


def test_v165_generator_mapping_preserves_existing_occluder_contract() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        nose = _render(session, "face.human_with_eyes_nose")
        mouth = _render(session, "face.human_with_eyes_nose_mouth")
    assert nose.visibility is not None
    assert mouth.visibility is not None
    assert nose.visibility.occluder_ids == ("nose",)
    assert mouth.visibility.occluder_ids == ("nose", "mouth")


def test_v165_unsupported_generator_does_not_acquire_overlap_proof() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _render(session, "face.human_with_eyes_nose_mouth_ears_hair")
        assert resolve_production_face_overlap_relations(
            root, result.camera_geometry, "future.unknown_generator",
            owner_geometry=extract_production_owner_geometry,
        ) is None


def test_v165_invalid_boundaries_fail_closed() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _render(session, GENERATORS[-1])
        with pytest.raises(TypeError, match="Component root"):
            resolve_production_face_overlap_relations(object(), result.camera_geometry, GENERATORS[-1], owner_geometry=extract_production_owner_geometry)  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="GeometryContract"):
            resolve_production_face_overlap_relations(root, object(), GENERATORS[-1], owner_geometry=extract_production_owner_geometry)  # type: ignore[arg-type]
        with pytest.raises(TypeError, match="non-empty string"):
            resolve_production_face_overlap_relations(root, result.camera_geometry, "", owner_geometry=extract_production_owner_geometry)
        with pytest.raises(TypeError, match="callable"):
            resolve_production_face_overlap_relations(root, result.camera_geometry, GENERATORS[-1], owner_geometry=object())  # type: ignore[arg-type]


def test_v165_invalid_owner_geometry_is_rejected_by_canonical_leaf() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _render(session, GENERATORS[-1])
        def bad_owner(geometry, owner_id):
            if owner_id == "face-01":
                return object(), math.nan
            return extract_production_owner_geometry(geometry, owner_id)
        with pytest.raises((TypeError, ValueError)):
            resolve_production_face_overlap_relations(root, result.camera_geometry, GENERATORS[-1], owner_geometry=bad_owner)


def test_v165_hidden_root_preserves_geometric_overlap_and_optical_visibility() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        visible = _render(session, GENERATORS[-1])
        old = root.visual
        root.visual = VisualContract(
            fill_color=old.fill_color, contour=old.contour, material=old.material,
            opacity=old.opacity, visibility=0.0,
        )
        hidden = _render(session, GENERATORS[-1])
    assert visible.visibility is not None and hidden.visibility is not None
    assert hidden.visibility.occluder_ids == visible.visibility.occluder_ids
    assert hidden.visibility.blocked_area == pytest.approx(visible.visibility.blocked_area)
    assert hidden.visibility.visible_area == pytest.approx(visible.visibility.visible_area)
