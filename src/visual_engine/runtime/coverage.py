from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Mapping

from visual_engine.components.common.geometry_contract import GeometryContract, GeometryPrimitive
from visual_engine.runtime.semantic_regions import RegionMap, SemanticRegion


class DepthRelation(str, Enum):
    FRONT = "front"
    BEHIND = "behind"
    COPLANAR = "coplanar"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class Occluder:
    """Generic spatial occluder. It deliberately has no object-type vocabulary."""

    occluder_id: str
    geometry: GeometryContract
    z: float = 0.0
    opacity: float = 1.0
    transmission: float = 0.0
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.occluder_id:
            raise ValueError("occluder_id must not be empty")
        if not math.isfinite(self.z):
            raise ValueError("occluder z must be finite")
        for name, value in (("opacity", self.opacity), ("transmission", self.transmission)):
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{name} must be in [0,1]")
        object.__setattr__(self, "metadata", dict(sorted(self.metadata.items())))


@dataclass(frozen=True, slots=True)
class RegionCoverage:
    region_id: str
    coverage: float
    visible: float
    transmitted_visibility: float
    depth_relation: DepthRelation

    def __post_init__(self) -> None:
        for name, value in (("coverage",self.coverage),("visible",self.visible),("transmitted_visibility",self.transmitted_visibility)):
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{name} must be in [0,1]")


@dataclass(frozen=True, slots=True)
class CoverageResult:
    target_id: str
    occluder_id: str
    regions: tuple[RegionCoverage, ...]
    overall_coverage: float
    depth_relation: DepthRelation
    consequences: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.target_id or not self.occluder_id:
            raise ValueError("CoverageResult IDs are required")
        if not 0 <= self.overall_coverage <= 1 or not math.isfinite(self.overall_coverage):
            raise ValueError("overall_coverage must be in [0,1]")
        object.__setattr__(self, "regions", tuple(sorted(self.regions, key=lambda r: r.region_id)))
        object.__setattr__(self, "consequences", tuple(sorted(set(self.consequences))))


_EPS = 1e-10


def _polygon_area(poly: list[tuple[float,float]]) -> float:
    if len(poly) < 3: return 0.0
    return abs(sum(poly[i][0]*poly[(i+1)%len(poly)][1]-poly[(i+1)%len(poly)][0]*poly[i][1] for i in range(len(poly)))) * 0.5


def _clip(subject: list[tuple[float,float]], a: tuple[float,float], b: tuple[float,float], ccw: bool) -> list[tuple[float,float]]:
    if not subject: return []
    def side(p): return (b[0]-a[0])*(p[1]-a[1])-(b[1]-a[1])*(p[0]-a[0])
    out=[]
    prev=subject[-1]; prev_in=(side(prev) >= -_EPS) if ccw else (side(prev) <= _EPS)
    for cur in subject:
        cur_in=(side(cur) >= -_EPS) if ccw else (side(cur) <= _EPS)
        if cur_in != prev_in:
            sp, sc = side(prev), side(cur)
            t = sp/(sp-sc) if abs(sp-sc)>_EPS else 0.0
            out.append((prev[0]+t*(cur[0]-prev[0]), prev[1]+t*(cur[1]-prev[1])))
        if cur_in: out.append(cur)
        prev, prev_in = cur, cur_in
    return out


def _convex_intersection_area(a: list[tuple[float,float]], b: list[tuple[float,float]]) -> float:
    if len(a)<3 or len(b)<3: return 0.0
    # Normalize clipping polygon orientation.
    if sum(b[i][0]*b[(i+1)%len(b)][1]-b[(i+1)%len(b)][0]*b[i][1] for i in range(len(b))) < 0:
        b=list(reversed(b))
    poly=a[:]
    for i in range(len(b)):
        poly=_clip(poly,b[i],b[(i+1)%len(b)],True)
        if not poly: return 0.0
    return _polygon_area(poly)


def _primitive_polygons(geometry: GeometryContract, ellipse_segments: int = 64) -> list[list[tuple[float,float]]]:
    result=[]
    for primitive in geometry.primitives:
        d=primitive.data
        if primitive.kind == "polygon" and "points" in d:
            pts=[(float(x),float(y)) for x,y in d["points"]]
            if len(pts)>=3: result.append(pts)
        elif primitive.kind in {"ellipse","circle"} and "cx" in d and "cy" in d:
            rx=ry=float(d.get("r", 0.0)) if "r" in d else (float(d.get("rx",0.0)), float(d.get("ry",0.0)))
            if isinstance(rx, tuple): erx,ery=rx
            else: erx=ery=rx
            angle=math.radians(float(d.get("rotation_deg",0.0)))
            ca,sa=math.cos(angle),math.sin(angle)
            result.append([(float(d["cx"])+erx*math.cos(2*math.pi*i/ellipse_segments)*ca-ery*math.sin(2*math.pi*i/ellipse_segments)*sa,
                            float(d["cy"])+erx*math.cos(2*math.pi*i/ellipse_segments)*sa+ery*math.sin(2*math.pi*i/ellipse_segments)*ca) for i in range(ellipse_segments)])
    return result


def _polygons(geometry: GeometryContract) -> list[list[tuple[float,float]]]:
    return _primitive_polygons(geometry)


def _depth_relation(target_z: float, occluder_z: float, epsilon: float = 1e-9) -> DepthRelation:
    if occluder_z > target_z + epsilon: return DepthRelation.FRONT
    if occluder_z < target_z - epsilon: return DepthRelation.BEHIND
    return DepthRelation.COPLANAR


def resolve_coverage(target_id: str, target_regions: RegionMap, occluder: Occluder, *, target_z: float = 0.0) -> CoverageResult:
    """Compatibility adapter over the authoritative multi-occluder visibility kernel.

    The old local clipping implementation could double-count overlapping primitives
    inside one occluder. Coverage now delegates to ``resolve_visibility`` so the
    legacy API inherits the overlap-safe boolean-union semantics.
    """
    from visual_engine.runtime.visibility import resolve_visibility

    result = resolve_visibility(target_id, target_regions, (occluder,), target_z=target_z)
    regions = tuple(
        RegionCoverage(
            item.region_id,
            item.coverage,
            item.visible,
            item.transmitted_visibility,
            item.depth_relation,
        )
        for item in result.regions
    )
    affected = tuple(f"covered:{item.region_id}" for item in regions if item.coverage > _EPS)
    depth = _depth_relation(target_z, occluder.z)
    return CoverageResult(
        target_id,
        occluder.occluder_id,
        regions,
        result.overall_coverage,
        depth,
        affected,
    )

