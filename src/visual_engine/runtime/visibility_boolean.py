from __future__ import annotations

"""Canonical planar boolean-composition contract for runtime visibility."""

from dataclasses import dataclass
from enum import Enum
from typing import Iterable

from shapely import ops as so

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.runtime.region_geometry import (
    RegionGeometry,
    _clean_polygon,
    geometry_to_region,
    region_to_contract,
)


class BooleanOperation(str, Enum):
    UNION = "union"
    INTERSECTION = "intersection"
    DIFFERENCE = "difference"


@dataclass(frozen=True, slots=True)
class BooleanResult:
    operation: BooleanOperation
    geometry: RegionGeometry
    area: float
    is_empty: bool


def boolean_operation(
    a: GeometryContract,
    b: GeometryContract,
    operation: BooleanOperation,
    *,
    ellipse_segments: int = 128,
) -> BooleanResult:
    """Compose two GeometryContract areas without renderer-specific semantics."""
    left = geometry_to_region(a, ellipse_segments=ellipse_segments)
    right = geometry_to_region(b, ellipse_segments=ellipse_segments)
    if operation is BooleanOperation.UNION:
        result = _clean_polygon(left.union(right))
    elif operation is BooleanOperation.INTERSECTION:
        result = _clean_polygon(left.intersection(right))
    elif operation is BooleanOperation.DIFFERENCE:
        result = _clean_polygon(left.difference(right))
    else:
        raise ValueError(f"unsupported boolean operation: {operation}")
    contract = region_to_contract(result, coordinate_frame=a.coordinate_frame)
    return BooleanResult(operation, contract, contract.area, result.is_empty)


def union_geometries(
    geometries: Iterable[GeometryContract], *, ellipse_segments: int = 128
) -> RegionGeometry:
    regions = [geometry_to_region(g, ellipse_segments=ellipse_segments) for g in geometries]
    regions = [region for region in regions if not region.is_empty]
    if not regions:
        return RegionGeometry()
    return region_to_contract(_clean_polygon(so.unary_union(regions)))


def intersection_geometry(
    a: GeometryContract, b: GeometryContract, *, ellipse_segments: int = 128
) -> RegionGeometry:
    left = geometry_to_region(a, ellipse_segments=ellipse_segments)
    right = geometry_to_region(b, ellipse_segments=ellipse_segments)
    return region_to_contract(_clean_polygon(left.intersection(right)), coordinate_frame=a.coordinate_frame)


def difference_geometry(
    a: GeometryContract, b: GeometryContract, *, ellipse_segments: int = 128
) -> RegionGeometry:
    left = geometry_to_region(a, ellipse_segments=ellipse_segments)
    right = geometry_to_region(b, ellipse_segments=ellipse_segments)
    return region_to_contract(_clean_polygon(left.difference(right)), coordinate_frame=a.coordinate_frame)
