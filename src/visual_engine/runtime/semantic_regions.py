from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Mapping

from visual_engine.components.common.geometry_contract import GeometryContract, GeometryPrimitive


class RegionKind(str, Enum):
    SEMANTIC = "semantic"
    SURFACE = "surface"
    SUBREGION = "subregion"


@dataclass(frozen=True, slots=True)
class SemanticRegion:
    """A named geometric region with no knowledge of what entity owns it."""

    region_id: str
    name: str
    geometry: GeometryContract
    kind: RegionKind = RegionKind.SEMANTIC
    parent_region_id: str | None = None
    tags: tuple[str, ...] = ()
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.region_id or not self.name:
            raise ValueError("SemanticRegion requires non-empty id and name")
        tags = tuple(sorted(set(self.tags)))
        if any(not isinstance(v, str) or not v for v in tags):
            raise ValueError("region tags must be non-empty strings")
        object.__setattr__(self, "tags", tags)
        object.__setattr__(self, "metadata", dict(sorted(self.metadata.items())))


@dataclass(frozen=True, slots=True)
class RegionMap:
    """Deterministic collection of semantic regions for one target component."""

    target_id: str
    regions: tuple[SemanticRegion, ...] = ()

    def __post_init__(self) -> None:
        if not self.target_id:
            raise ValueError("RegionMap target_id must not be empty")
        ids = [r.region_id for r in self.regions]
        if len(ids) != len(set(ids)):
            raise ValueError("Region IDs must be unique")
        object.__setattr__(self, "regions", tuple(sorted(self.regions, key=lambda r: r.region_id)))

    def get(self, region_id: str) -> SemanticRegion:
        for region in self.regions:
            if region.region_id == region_id:
                return region
        raise KeyError(region_id)

    def by_name(self, name: str) -> tuple[SemanticRegion, ...]:
        return tuple(r for r in self.regions if r.name == name)


def rectangle_region(region_id: str, name: str, min_x: float, min_y: float, max_x: float, max_y: float, **kwargs) -> SemanticRegion:
    from visual_engine.components.common.geometry_contract import GeometryBounds
    if max_x < min_x or max_y < min_y:
        raise ValueError("region rectangle must have max >= min")
    geometry = GeometryContract(
        bounds=GeometryBounds(min_x, min_y, max_x, max_y),
        primitives=(GeometryPrimitive("polygon", {"points": ((min_x,min_y),(max_x,min_y),(max_x,max_y),(min_x,max_y))}),),
    )
    return SemanticRegion(region_id, name, geometry, **kwargs)


def polygon_region(region_id: str, name: str, points: tuple[tuple[float,float], ...], **kwargs) -> SemanticRegion:
    if len(points) < 3:
        raise ValueError("polygon region requires at least three points")
    xs, ys = zip(*points)
    from visual_engine.components.common.geometry_contract import GeometryBounds
    geometry = GeometryContract(
        bounds=GeometryBounds(min(xs), min(ys), max(xs), max(ys)),
        primitives=(GeometryPrimitive("polygon", {"points": points}),),
    )
    return SemanticRegion(region_id, name, geometry, **kwargs)
