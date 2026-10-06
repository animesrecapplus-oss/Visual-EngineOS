from __future__ import annotations

from pathlib import Path

import pytest

from visual_engine.components.common.geometry_contract import GeometryBounds, GeometryContract, GeometryPath
from visual_engine.runtime import transform_geometry_contract as public_transform
from visual_engine.runtime.geometry_contract_transform import transform_geometry_contract
from visual_engine.runtime.geometry_transform import transform_geometry_contract as legacy_transform


ROOT = Path(__file__).parents[2]


def _geometry() -> GeometryContract:
    return GeometryContract(
        coordinate_frame="local",
        bounds=GeometryBounds(0.0, 0.0, 2.0, 1.0),
        paths=(GeometryPath((("M", (0.0, 0.0)), ("L", (2.0, 0.0)), ("L", (2.0, 1.0)))),),
        anchors={"center": (1.0, 0.5, 0.25)},
        local_z=0.25,
    )


def test_single_owner_preserves_public_and_legacy_api() -> None:
    assert public_transform is transform_geometry_contract
    assert legacy_transform is transform_geometry_contract


def test_transform_contract_preserves_semantic_metadata_and_moves_geometry() -> None:
    matrix = ((2.0, 0.0, 10.0), (0.0, 3.0, -2.0), (0.0, 0.0, 1.0))
    transformed = transform_geometry_contract(_geometry(), matrix, z_offset=1.5, coordinate_frame="camera")

    assert transformed.coordinate_frame == "camera"
    assert transformed.bounds == GeometryBounds(10.0, -2.0, 14.0, 1.0)
    assert transformed.paths[0].commands[0] == ("M", (10.0, -2.0))
    assert transformed.paths[0].commands[-1] == ("L", (14.0, 1.0))
    assert transformed.anchors["center"] == (12.0, -0.5, 1.75)
    assert transformed.local_z == 1.75


def test_transform_contract_rejects_non_finite_and_singular_matrices() -> None:
    with pytest.raises(ValueError, match="must be finite"):
        transform_geometry_contract(_geometry(), ((float("nan"), 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)))
    with pytest.raises(ValueError, match="must be invertible"):
        transform_geometry_contract(_geometry(), ((1.0, 0.0, 0.0), (0.0, 0.0, 0.0), (0.0, 0.0, 1.0)))


def test_geometry_transform_module_now_owns_resolution_only() -> None:
    source = (ROOT / "src/visual_engine/runtime/geometry_transform.py").read_text()
    assert "def _transform_primitive" not in source
    assert "def _transform_path" not in source
    assert "def _ellipse_axes" not in source
    assert "def transform_geometry_contract" not in source
    assert "from visual_engine.runtime.geometry_contract_transform import Matrix3, transform_geometry_contract" in source


def test_extracted_module_is_renderer_independent() -> None:
    source = (ROOT / "src/visual_engine/runtime/geometry_contract_transform.py").read_text()
    assert "visual_engine.render" not in source
    assert "svg" not in source.lower()
