from __future__ import annotations

import ast

import pytest

from visual_engine.components.common.geometry_contract import GeometryContract, GeometryPath, GeometrySurface
from visual_engine.entities import build_human_face
from visual_engine.runtime import ProductionRenderSession, extract_production_owner_geometry
from visual_engine.scene.composition import Camera, Placement
from visual_engine.math import Vec2


def _request(session: ProductionRenderSession):
    return session.render_face(
        "face-01", placement=Placement("face-01", Vec2(450.0, 450.0), scale=650.0),
        camera=Camera(), generator="face.human_with_eyes_nose_mouth_ears_hair",
    )


def test_v162_real_production_owners_extract_with_expected_depths() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
        head, head_depth = extract_production_owner_geometry(result.camera_geometry, "face-01")
        hair, hair_depth = extract_production_owner_geometry(result.camera_geometry, "hair")
        left_ear, ear_depth = extract_production_owner_geometry(result.camera_geometry, "left_ear")
    assert head.surfaces and hair.surfaces and left_ear.surfaces
    assert (head_depth, hair_depth, ear_depth) == (0.0, 1.0, 0.0)


def test_v162_rebases_selected_surface_paths_deterministically() -> None:
    geometry = GeometryContract(
        paths=(GeometryPath((("M", (0.0, 0.0)),)), GeometryPath((("M", (1.0, 1.0)),))),
        surfaces=(
            GeometrySurface("a", {"source_component_id": "owner", "depth_layer": 2, "path_index": 1}),
            GeometrySurface("b", {"source_component_id": "owner", "depth_layer": 2, "path_index": 0}),
        ),
    )
    extracted, depth = extract_production_owner_geometry(geometry, "owner")
    assert depth == 2.0
    assert [surface.data["path_index"] for surface in extracted.surfaces] == [0, 1]
    assert extracted.paths == (geometry.paths[1], geometry.paths[0])


def test_v162_rejects_invalid_boundary_inputs() -> None:
    with pytest.raises(TypeError):
        extract_production_owner_geometry(object(), "owner")  # type: ignore[arg-type]
    geometry = GeometryContract()
    with pytest.raises(ValueError):
        extract_production_owner_geometry(geometry, "")
    with pytest.raises(ValueError):
        extract_production_owner_geometry(geometry, "missing")


def test_v162_rejects_missing_or_conflicting_depth() -> None:
    missing = GeometryContract(surfaces=(GeometrySurface("x", {"source_component_id": "owner"}),))
    conflicting = GeometryContract(surfaces=(
        GeometrySurface("a", {"source_component_id": "owner", "depth_layer": 0}),
        GeometrySurface("b", {"source_component_id": "owner", "depth_layer": 1}),
    ))
    with pytest.raises(ValueError, match="explicit depth_layer"):
        extract_production_owner_geometry(missing, "owner")
    with pytest.raises(ValueError, match="inconsistent depth layers"):
        extract_production_owner_geometry(conflicting, "owner")


def test_v162_rejects_invalid_surface_path() -> None:
    geometry = GeometryContract(
        surfaces=(GeometrySurface("bad", {"source_component_id": "owner", "depth_layer": 0, "path_index": 9}),)
    )
    with pytest.raises(ValueError, match="invalid path index"):
        extract_production_owner_geometry(geometry, "owner")


def test_v162_production_slice_has_no_duplicate_owner_helper() -> None:
    source = open("src/visual_engine/runtime/production_face_render.py", encoding="utf-8").read()
    tree = ast.parse(source)
    assert not any(isinstance(node, ast.FunctionDef) and node.name == "_owner_geometry" for node in tree.body)
    assert "extract_production_owner_geometry" in source
