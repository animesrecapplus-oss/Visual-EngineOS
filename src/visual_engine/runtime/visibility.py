from __future__ import annotations

"""Deterministic multi-occluder visibility kernel.

Planar region materialization lives in ``region_geometry`` and boolean
composition lives in ``visibility_boolean``; this module owns depth filtering,
optical visibility and structured event emission.
"""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Iterable, Mapping

from shapely import geometry as sg
from shapely import ops as so

from visual_engine.runtime.coverage import DepthRelation, Occluder, _depth_relation
from visual_engine.runtime.semantic_regions import RegionMap
# These imports preserve historical visibility/region public names; region_geometry remains their canonical owner.
from visual_engine.runtime.region_geometry import (
    BooleanPolygon, RegionGeometry, _clean_polygon, geometry_to_region, path_to_region,
    primitive_to_region, region_to_contract,
)
from visual_engine.runtime.visibility_boolean import (
    BooleanOperation, BooleanResult, boolean_operation, difference_geometry,
    intersection_geometry, union_geometries,
)

_EPS = 1e-9


class VisibilityEventKind(str, Enum):
    COVERAGE = "coverage"
    VISIBILITY = "visibility"
    TRANSMISSION = "transmission"
    DEPTH = "depth"


@dataclass(frozen=True, slots=True)
class AffectedRegionEvent:
    """Structured downstream event; no anatomy/object vocabulary is assumed."""

    target_id: str
    region_id: str
    occluder_id: str
    kind: VisibilityEventKind
    coverage: float
    visible: float
    transmitted_visibility: float
    depth_relation: DepthRelation
    intersection_area: float
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.target_id or not self.region_id or not self.occluder_id:
            raise ValueError("visibility event IDs are required")
        for name, value in (("coverage", self.coverage), ("visible", self.visible),
                            ("transmitted_visibility", self.transmitted_visibility)):
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{name} must be in [0,1]")
        if self.intersection_area < 0 or not math.isfinite(self.intersection_area):
            raise ValueError("intersection_area must be finite and >= 0")
        object.__setattr__(self, "metadata", dict(sorted(self.metadata.items())))


@dataclass(frozen=True, slots=True)
class VisibilityRegionResult:
    region_id: str
    area: float
    coverage: float
    visible: float
    transmitted_visibility: float
    depth_relation: DepthRelation
    blocked_area: float
    transmission_area: float


@dataclass(frozen=True, slots=True)
class VisibilityResult:
    target_id: str
    regions: tuple[VisibilityRegionResult, ...]
    overall_coverage: float
    overall_visible: float
    events: tuple[AffectedRegionEvent, ...]

    def __post_init__(self) -> None:
        if not self.target_id:
            raise ValueError("target_id is required")
        for name, value in (("overall_coverage", self.overall_coverage), ("overall_visible", self.overall_visible)):
            if not math.isfinite(value) or not 0 <= value <= 1:
                raise ValueError(f"{name} must be in [0,1]")
        object.__setattr__(self, "regions", tuple(sorted(self.regions, key=lambda x: x.region_id)))
        object.__setattr__(self, "events", tuple(sorted(self.events, key=lambda x: (x.region_id, x.occluder_id, x.kind.value))))


def _effective_optical_visibility(occluders: tuple[Occluder, ...]) -> float:
    """Visibility of target light through ordered front occluders at a point.

    ``opacity`` is the amount of incident light affected by the layer. The
    transmitted fraction of that affected light is ``transmission``. Thus the
    effective blocking alpha is opacity * (1 - transmission).
    """
    transmission = 1.0
    for occluder in occluders:
        transmission *= 1.0 - occluder.opacity * (1.0 - occluder.transmission)
    return min(1.0, max(0.0, transmission))


def resolve_visibility(
    target_id: str,
    target_regions: RegionMap,
    occluders: Iterable[Occluder],
    *,
    target_z: float = 0.0,
    coplanar_occludes: bool = False,
    ellipse_segments: int = 128,
) -> VisibilityResult:
    """Resolve true multi-occluder visibility with overlap-safe boolean geometry.

    Coverage is the union of all front occluder intersections, so overlapping
    occluders never double-count area. Optical visibility is separately reduced
    by front-to-back layer compositing. Transmission is reported independently.
    """
    ordered = tuple(sorted(occluders, key=lambda o: (-o.z, o.occluder_id)))
    front = tuple(o for o in ordered if _depth_relation(target_z, o.z) is DepthRelation.FRONT or
                  (coplanar_occludes and _depth_relation(target_z, o.z) is DepthRelation.COPLANAR))
    results = []
    events = []
    total_area = 0.0
    total_blocked = 0.0
    total_visible = 0.0

    for region in target_regions.regions:
        target = geometry_to_region(region.geometry, ellipse_segments=ellipse_segments)
        area = max(0.0, float(target.area))
        total_area += area
        if area <= _EPS:
            results.append(VisibilityRegionResult(
                region.region_id, area, 0.0, 1.0, 0.0,
                DepthRelation.UNKNOWN if not front else DepthRelation.BEHIND,
                0.0, 0.0,
            ))
            continue
        if not front:
            # No front occluder means the complete target area is visible.
            # Keep the global aggregate consistent with the per-region result.
            visibility = 1.0
            results.append(VisibilityRegionResult(
                region.region_id, area, 0.0, visibility, 0.0,
                DepthRelation.UNKNOWN, 0.0, 0.0,
            ))
            total_visible += area
            continue

        intersections = []
        event_pairs = []
        # Materialize each front occluder region once per target region. The cell
        # arrangement below can contain many polygons; rebuilding the same Shapely
        # geometry inside every cell would turn visibility into an avoidable hot path.
        front_regions = {
            occluder.occluder_id: geometry_to_region(occluder.geometry, ellipse_segments=ellipse_segments)
            for occluder in front
        }
        for occluder in front:
            occ = front_regions[occluder.occluder_id]
            inter = target.intersection(occ)
            if not inter.is_empty and inter.area > _EPS:
                intersections.append(inter)
                event_pairs.append((occluder, inter))

        covered = _clean_polygon(so.unary_union(intersections)) if intersections else sg.GeometryCollection()
        blocked_area = min(area, max(0.0, float(covered.area)))
        coverage = blocked_area / area

        # Build a planar arrangement from the target boundary and all occluder
        # boundaries. Each cell receives the optical stack that contains it.
        boundaries = [target.boundary]
        boundaries.extend(i.boundary for i in intersections)
        cells = []
        if boundaries:
            try:
                pieces = so.polygonize(so.unary_union(boundaries))
                for cell in pieces:
                    clipped = cell.intersection(target)
                    if not clipped.is_empty and clipped.area > _EPS:
                        cells.append(clipped)
            except Exception:
                cells = []

        if not cells:
            cells = [target]

        visible_area = 0.0
        transmitted_area = 0.0
        for cell in cells:
            point = cell.representative_point()
            stack = tuple(o for o in front if front_regions[o.occluder_id].contains(point))
            if not stack:
                local_visibility = 1.0
                local_transmitted = 0.0
            else:
                local_visibility = _effective_optical_visibility(stack)
                # Portion of target light reaching the camera through at least
                # one transmissive layer, kept separate from geometric coverage.
                local_transmitted = max(0.0, local_visibility)
            visible_area += cell.area * local_visibility
            transmitted_area += cell.area * local_transmitted if stack else 0.0

        visible = min(1.0, max(0.0, visible_area / area))
        transmission = min(1.0, max(0.0, transmitted_area / area))
        # Preserve the actual nearest occluder relation. A coplanar occluder may
        # participate when explicitly enabled; it must not be relabelled FRONT.
        nearest_z = max(occluder.z for occluder in front)
        depth = _depth_relation(target_z, nearest_z)
        results.append(VisibilityRegionResult(region.region_id, area, coverage, visible, transmission,
                                              depth, blocked_area, transmitted_area))
        total_blocked += blocked_area
        total_visible += visible_area

        for occluder, inter in event_pairs:
            pair_coverage = min(1.0, max(0.0, float(inter.area) / area))
            events.append(AffectedRegionEvent(
                target_id, region.region_id, occluder.occluder_id,
                VisibilityEventKind.COVERAGE, pair_coverage, visible, transmission,
                _depth_relation(target_z, occluder.z), float(inter.area),
            ))
            events.append(AffectedRegionEvent(
                target_id, region.region_id, occluder.occluder_id,
                VisibilityEventKind.VISIBILITY, pair_coverage, visible, transmission,
                _depth_relation(target_z, occluder.z), float(inter.area),
            ))
            if occluder.transmission > 0.0 or occluder.opacity < 1.0:
                events.append(AffectedRegionEvent(
                    target_id, region.region_id, occluder.occluder_id,
                    VisibilityEventKind.TRANSMISSION, pair_coverage, visible, transmission,
                    _depth_relation(target_z, occluder.z), float(inter.area),
                ))
            events.append(AffectedRegionEvent(
                target_id, region.region_id, occluder.occluder_id,
                VisibilityEventKind.DEPTH, pair_coverage, visible, transmission,
                _depth_relation(target_z, occluder.z), float(inter.area),
            ))

    overall_coverage = total_blocked / total_area if total_area > _EPS else 0.0
    overall_visible = total_visible / total_area if total_area > _EPS else 1.0
    # Boolean geometry can accumulate a few ulps when a front occluder has no
    # intersection at all. The public contract is a closed probability interval,
    # so clamp only the final aggregate rather than hiding intermediate geometry.
    overall_coverage = min(1.0, max(0.0, overall_coverage))
    overall_visible = min(1.0, max(0.0, overall_visible))
    return VisibilityResult(target_id, tuple(results), overall_coverage, overall_visible, tuple(events))
