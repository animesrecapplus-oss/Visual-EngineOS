from __future__ import annotations

import importlib
from pathlib import Path

from visual_engine.components.common.geometry_contract import GeometryContract, GeometryPath, GeometryPrimitive
from visual_engine.runtime import (
    BooleanPolygon,
    RegionGeometry,
    geometry_to_region,
    path_to_region,
    region_to_contract,
)
from visual_engine.runtime.region_geometry import (
    BooleanPolygon as RegionBooleanPolygon,
    RegionGeometry as RegionGeometryOwner,
    geometry_to_region as owned_geometry_to_region,
    path_to_region as owned_path_to_region,
    region_to_contract as owned_region_to_contract,
)


ROOT = Path(__file__).resolve().parents[2]


def _rect(x0: float, y0: float, x1: float, y1: float) -> GeometryContract:
    return GeometryContract(
        coordinate_frame="scene",
        primitives=(
            GeometryPrimitive("polygon", {"points": ((x0, y0), (x1, y0), (x1, y1), (x0, y1))}),
        ),
    )


def test_region_types_and_converters_have_one_owner() -> None:
    assert BooleanPolygon is RegionBooleanPolygon
    assert RegionGeometry is RegionGeometryOwner
    assert geometry_to_region is owned_geometry_to_region
    assert path_to_region is owned_path_to_region
    assert region_to_contract is owned_region_to_contract


def test_legacy_visibility_imports_remain_compatible() -> None:
    legacy = importlib.import_module("visual_engine.runtime.visibility")
    owner = importlib.import_module("visual_engine.runtime.region_geometry")
    assert legacy.geometry_to_region is owner.geometry_to_region
    assert legacy.path_to_region is owner.path_to_region
    assert legacy.region_to_contract is owner.region_to_contract


def test_region_conversion_remains_deterministic() -> None:
    geometry = _rect(0.0, 0.0, 10.0, 5.0)
    first = geometry_to_region(geometry)
    second = geometry_to_region(geometry)
    assert first.equals(second)
    assert first.area == 50.0


def test_closed_bezier_path_remains_an_area_region() -> None:
    path = GeometryPath((
        ("M", (0.0, 0.0)),
        ("C", (2.0, 0.0, 8.0, 0.0, 10.0, 0.0)),
        ("L", (10.0, 5.0)),
        ("L", (0.0, 5.0)),
        ("Z", ()),
    ))
    region = path_to_region(path)
    assert not region.is_empty
    assert region.area > 0.0


def test_region_contract_preserves_holes() -> None:
    from shapely.geometry import Polygon

    region = Polygon(
        ((0.0, 0.0), (10.0, 0.0), (10.0, 10.0), (0.0, 10.0)),
        holes=(((2.0, 2.0), (8.0, 2.0), (8.0, 8.0), (2.0, 8.0)),),
    )
    contract = region_to_contract(region)
    assert len(contract.polygons) == 1
    assert len(contract.polygons[0].holes) == 1
    assert contract.area == 64.0


def test_visibility_module_keeps_boolean_and_visibility_responsibilities() -> None:
    visibility = importlib.import_module("visual_engine.runtime.visibility")
    assert hasattr(visibility, "boolean_operation")
    assert hasattr(visibility, "resolve_visibility")
    assert not hasattr(visibility, "_path_points")
    assert not hasattr(visibility, "_ellipse_polygon")
