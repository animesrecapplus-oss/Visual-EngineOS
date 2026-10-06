from __future__ import annotations

"""Causal attribution for multi-occluder planar visibility.

This module does not decide *what* an object is. It partitions the target's
planar area into regions with a stable occlusion stack and derives explicit,
non-additive attribution measures from that partition.

The contracts deliberately distinguish:
- geometric coverage: where an occluder intersects the target;
- exclusive coverage: area covered by one occluder and no other front occluder;
- shared coverage: area where the occluder overlaps at least one other;
- dominant coverage: area for which the occluder is the nearest front layer;
- marginal optical loss: the change in visibility when that occluder is removed
  while every other layer remains unchanged.

No attribution value is silently treated as an additive decomposition of total
coverage. This is essential for overlapping and transmissive layers.
"""

from dataclasses import dataclass
from enum import Enum
import math
from typing import Iterable

from shapely import geometry as sg
from shapely import ops as so

from visual_engine.runtime.coverage import DepthRelation, Occluder, _depth_relation
from visual_engine.runtime.semantic_regions import RegionMap
from visual_engine.runtime.visibility import _EPS
from visual_engine.runtime.region_geometry import _clean_polygon, geometry_to_region


class AttributionKind(str, Enum):
    """Semantic meaning of an attribution measurement."""

    GEOMETRIC = "geometric"
    EXCLUSIVE = "exclusive"
    SHARED = "shared"
    DOMINANT = "dominant"
    OPTICAL_MARGINAL = "optical_marginal"


@dataclass(frozen=True, slots=True)
class OccluderAttribution:
    """Attribution metrics for one occluder within one target region.

    ``coverage`` is pairwise geometric intersection and therefore may overlap
    with another occluder's coverage.
    ``exclusive_coverage`` and ``dominant_coverage`` are disjoint spatial
    measures within the target region, but they answer different questions.
    ``optical_marginal_loss`` is a counterfactual visibility delta and is not
    required to sum to the total optical loss across occluders.
    """

    target_id: str
    region_id: str
    occluder_id: str
    coverage: float
    exclusive_coverage: float
    shared_coverage: float
    dominant_coverage: float
    optical_marginal_loss: float
    intersection_area: float
    exclusive_area: float
    shared_area: float
    dominant_area: float
    depth_relation: DepthRelation

    def __post_init__(self) -> None:
        if not self.target_id or not self.region_id or not self.occluder_id:
            raise ValueError("attribution IDs are required")
        for name, value in (
            ("coverage", self.coverage),
            ("exclusive_coverage", self.exclusive_coverage),
            ("shared_coverage", self.shared_coverage),
            ("dominant_coverage", self.dominant_coverage),
            ("optical_marginal_loss", self.optical_marginal_loss),
        ):
            if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be in [0,1]")
        for name, value in (
            ("intersection_area", self.intersection_area),
            ("exclusive_area", self.exclusive_area),
            ("shared_area", self.shared_area),
            ("dominant_area", self.dominant_area),
        ):
            if not math.isfinite(value) or value < 0.0:
                raise ValueError(f"{name} must be finite and >= 0")
        if self.exclusive_coverage + self.shared_coverage > self.coverage + 1e-8:
            raise ValueError("exclusive + shared coverage cannot exceed geometric coverage")
        if self.dominant_coverage > self.coverage + 1e-8:
            raise ValueError("dominant coverage cannot exceed geometric coverage")


@dataclass(frozen=True, slots=True)
class VisibilityAttributionResult:
    """Complete multi-occluder attribution for one target."""

    target_id: str
    regions: tuple[tuple[str, tuple[OccluderAttribution, ...]], ...]

    @property
    def attributions(self) -> tuple[OccluderAttribution, ...]:
        return tuple(item for _, values in self.regions for item in values)

    def __post_init__(self) -> None:
        if not self.target_id:
            raise ValueError("target_id is required")
        normalized = []
        seen_regions: set[str] = set()
        for region_id, values in self.regions:
            if not region_id or region_id in seen_regions:
                raise ValueError("region IDs must be non-empty and unique")
            seen_regions.add(region_id)
            normalized.append((region_id, tuple(sorted(values, key=lambda x: x.occluder_id))))
        object.__setattr__(self, "regions", tuple(sorted(normalized, key=lambda x: x[0])))


def _ordered_front_occluders(
    occluders: Iterable[Occluder],
    *,
    target_z: float,
    coplanar_occludes: bool,
) -> tuple[Occluder, ...]:
    ordered = tuple(sorted(occluders, key=lambda o: (-o.z, o.occluder_id)))
    return tuple(
        o for o in ordered
        if _depth_relation(target_z, o.z) is DepthRelation.FRONT
        or (coplanar_occludes and _depth_relation(target_z, o.z) is DepthRelation.COPLANAR)
    )


def _build_cells(target: sg.base.BaseGeometry, intersections: dict[str, sg.base.BaseGeometry]) -> tuple[sg.base.BaseGeometry, ...]:
    """Create an overlap-safe planar arrangement clipped to the target."""
    boundaries = [target.boundary]
    boundaries.extend(geometry.boundary for geometry in intersections.values() if not geometry.is_empty)
    if not boundaries:
        return (target,)
    try:
        pieces = so.polygonize(so.unary_union(boundaries))
        cells = []
        for piece in pieces:
            clipped = piece.intersection(target)
            if not clipped.is_empty and clipped.area > _EPS:
                cells.append(_clean_polygon(clipped))
        cells.sort(key=lambda g: (round(float(g.area), 12), g.wkb_hex))
        return tuple(cells) if cells else (target,)
    except Exception:
        # Attribution must fail closed rather than invent a partition.
        raise RuntimeError("unable to construct deterministic visibility arrangement")


def _optical_visibility(stack: tuple[Occluder, ...]) -> float:
    visibility = 1.0
    for occluder in stack:
        visibility *= 1.0 - occluder.opacity * (1.0 - occluder.transmission)
    return min(1.0, max(0.0, visibility))


def resolve_visibility_attribution(
    target_id: str,
    target_regions: RegionMap,
    occluders: Iterable[Occluder],
    *,
    target_z: float = 0.0,
    coplanar_occludes: bool = False,
    ellipse_segments: int = 128,
) -> VisibilityAttributionResult:
    """Resolve geometric and optical attribution for multiple occluders.

    For every target region the target plane is partitioned by all front
    occluder boundaries. Each cell receives an ordered depth stack.

    Attribution definitions:
      * coverage: target ∩ occluder / target area.
      * exclusive: covered by this occluder and by no other front occluder.
      * shared: covered by this occluder and at least one other front occluder.
      * dominant: this occluder is the nearest front layer in the cell.
      * optical_marginal_loss: visibility_without_this - visibility_with_all,
        integrated over the target. It is a counterfactual and intentionally
        non-additive across occluders.

    Duplicate occluder IDs are rejected because attribution would otherwise be
    ambiguous. The input geometry frames must match the target region frame.
    """
    if not target_id or target_regions.target_id != target_id:
        raise ValueError("target_id must match target RegionMap")

    front = _ordered_front_occluders(
        occluders, target_z=target_z, coplanar_occludes=coplanar_occludes
    )
    ids = [o.occluder_id for o in front]
    if len(ids) != len(set(ids)):
        raise ValueError("occluder IDs must be unique")

    results: list[tuple[str, tuple[OccluderAttribution, ...]]] = []
    for region in target_regions.regions:
        target = geometry_to_region(region.geometry, ellipse_segments=ellipse_segments)
        area = float(target.area)
        if area <= _EPS or not front:
            results.append((region.region_id, ()))
            continue

        geometries = {
            o.occluder_id: geometry_to_region(o.geometry, ellipse_segments=ellipse_segments)
            for o in front
        }
        intersections = {
            oid: _clean_polygon(target.intersection(geometry))
            for oid, geometry in geometries.items()
        }
        intersections = {oid: g for oid, g in intersections.items() if not g.is_empty and g.area > _EPS}
        cells = _build_cells(target, intersections)

        # Pairwise geometric metrics are computed directly from exact boolean
        # intersections; cells are used for overlap/dominance and optical effects.
        pairwise_area = {oid: float(g.area) for oid, g in intersections.items()}

        exclusive_area = {o.occluder_id: 0.0 for o in front}
        shared_area = {o.occluder_id: 0.0 for o in front}
        dominant_area = {o.occluder_id: 0.0 for o in front}
        marginal_loss_area = {o.occluder_id: 0.0 for o in front}

        for cell in cells:
            point = cell.representative_point()
            stack = tuple(o for o in front if geometries[o.occluder_id].covers(point))
            if not stack:
                continue
            cell_area = float(cell.area)
            if len(stack) == 1:
                exclusive_area[stack[0].occluder_id] += cell_area
            else:
                for o in stack:
                    shared_area[o.occluder_id] += cell_area
            # Sorted front is descending z: first is the visually nearest layer.
            dominant_area[stack[0].occluder_id] += cell_area

            with_all = _optical_visibility(stack)
            for o in stack:
                without = _optical_visibility(tuple(other for other in stack if other.occluder_id != o.occluder_id))
                marginal_loss_area[o.occluder_id] += cell_area * max(0.0, without - with_all)

        attrs = []
        for o in front:
            oid = o.occluder_id
            intersection = pairwise_area.get(oid, 0.0)
            exclusive = min(intersection, exclusive_area[oid])
            shared = min(intersection, shared_area[oid])
            dominant = min(intersection, dominant_area[oid])
            attrs.append(
                OccluderAttribution(
                    target_id=target_id,
                    region_id=region.region_id,
                    occluder_id=oid,
                    coverage=min(1.0, intersection / area),
                    exclusive_coverage=min(1.0, exclusive / area),
                    shared_coverage=min(1.0, shared / area),
                    dominant_coverage=min(1.0, dominant / area),
                    optical_marginal_loss=min(1.0, marginal_loss_area[oid] / area),
                    intersection_area=intersection,
                    exclusive_area=exclusive,
                    shared_area=shared,
                    dominant_area=dominant,
                    depth_relation=_depth_relation(target_z, o.z),
                )
            )
        results.append((region.region_id, tuple(attrs)))

    return VisibilityAttributionResult(target_id, tuple(results))
