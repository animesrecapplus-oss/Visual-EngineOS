from __future__ import annotations

import math

import pytest

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.entities import build_human_face
from visual_engine.runtime import ProductionRenderSession, ProductionVisibilityResolution, resolve_face_overlap_visibility
from visual_engine.runtime import extract_production_owner_geometry
from visual_engine.scene.composition import Camera, Placement
from visual_engine.math import Vec2


def _request(session: ProductionRenderSession):
    return session.render_face(
        "face-01", placement=Placement("face-01", Vec2(450.0, 450.0), scale=650.0),
        camera=Camera(), generator="face.human_with_eyes_nose_mouth",
    )


def test_v160_extracted_owner_preserves_real_head_nose_mouth_proof() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
    assert isinstance(result.visibility, ProductionVisibilityResolution)
    assert result.visibility.occluder_ids == ("nose", "mouth")
    assert result.visibility.visibility.overall_coverage > 0.0
    assert result.visibility.visibility.overall_visible < 1.0


def test_v160_public_resolver_matches_session_result() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
        direct = resolve_face_overlap_visibility(
            root, result.camera_geometry, ("nose", "mouth"), owner_geometry=extract_production_owner_geometry,
        )
    assert direct.visibility == result.visibility.visibility
    assert direct.attribution == result.visibility.attribution


def test_v160_rejects_invalid_inputs_before_geometry_resolution() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
        owner = extract_production_owner_geometry
        with pytest.raises(TypeError):
            resolve_face_overlap_visibility("bad", result.camera_geometry, ("nose",), owner_geometry=owner)  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            resolve_face_overlap_visibility(root, object(), ("nose",), owner_geometry=owner)  # type: ignore[arg-type]
        with pytest.raises(TypeError):
            resolve_face_overlap_visibility(root, result.camera_geometry, ("nose",), owner_geometry=None)  # type: ignore[arg-type]
        with pytest.raises(ValueError):
            resolve_face_overlap_visibility(root, result.camera_geometry, ("nose", "nose"), owner_geometry=owner)
        with pytest.raises(ValueError):
            resolve_face_overlap_visibility(root, result.camera_geometry, ("",), owner_geometry=owner)


def test_v160_missing_or_unknown_child_is_fail_closed() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
        owner = extract_production_owner_geometry
        with pytest.raises(ValueError, match="requires component 'ghost'"):
            resolve_face_overlap_visibility(root, result.camera_geometry, ("ghost",), owner_geometry=owner)


def test_v160_owner_contract_rejects_non_geometry_return() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
        def broken_owner(_geometry, _owner_id):
            return GeometryContract(), math.nan
        with pytest.raises(ValueError):
            resolve_face_overlap_visibility(root, result.camera_geometry, ("nose",), owner_geometry=broken_owner)
