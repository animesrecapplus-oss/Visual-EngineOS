from __future__ import annotations

"""Coverage-specific contract and deterministic geometric scale solver."""

from dataclasses import dataclass
import math

from shapely import affinity
from shapely.geometry import Point
_EPS = 1e-9
@dataclass(frozen=True, slots=True)
class CoverageIntent:
    """Requested fraction of target area to be geometrically covered by source."""

    target_fraction: float
    tolerance: float = 1e-3
    max_iterations: int = 48

    def __post_init__(self) -> None:
        # Reject non-finite ratios before the numerical search reaches Shapely.
        if not math.isfinite(self.target_fraction) or not 0.0 <= self.target_fraction <= 1.0:
            raise ValueError("target_fraction must be in [0,1]")
        if not math.isfinite(self.tolerance) or self.tolerance <= 0 or self.tolerance >= 1:
            raise ValueError("coverage tolerance must be in (0,1)")
        if self.max_iterations < 8:
            raise ValueError("coverage max_iterations must be >= 8")
def _place_region(
    region,
    source_anchor: tuple[float, float, float],
    target_anchor: tuple[float, float, float],
    scale_x: float,
    scale_y: float,
    rotation_deg: float,
    offset_x: float,
    offset_y: float,
):
    """Apply PlacementSolution transform semantics around the source anchor."""
    # The anchor-centered transform is the invariant shared with PlacementSolution:
    # scale/rotate first, then translate the transformed anchor to the target anchor.
    placed = affinity.scale(
        region, xfact=scale_x, yfact=scale_y,
        origin=(source_anchor[0], source_anchor[1]),
    )
    placed = affinity.rotate(placed, rotation_deg, origin=(source_anchor[0], source_anchor[1]))
    return affinity.translate(
        placed,
        xoff=target_anchor[0] + offset_x - source_anchor[0],
        yoff=target_anchor[1] + offset_y - source_anchor[1],
    )

def _coverage_for_scale(
    source_region,
    target_region,
    source_anchor,
    target_anchor,
    scale: float,
    rotation_deg: float,
    offset_x: float,
    offset_y: float,
) -> float:
    """Measure target-area coverage after applying one uniform scale."""
    placed = _place_region(
        source_region, source_anchor, target_anchor, scale, scale,
        rotation_deg, offset_x, offset_y,
    )
    return min(1.0, max(0.0, float(placed.intersection(target_region).area) / float(target_region.area)))

def _finite_triplet(value: tuple[float, float, float], name: str) -> tuple[float, float, float]:
    try:
        point = tuple(float(v) for v in value)
    except (TypeError, ValueError) as exc:
        raise TypeError(f"{name} must contain three numeric values") from exc
    if len(point) != 3 or not all(math.isfinite(v) for v in point):
        raise ValueError(f"{name} must contain finite x/y/z")
    return point  # type: ignore[return-value]

def resolve_coverage_scale(
    source_region,
    target_region,
    source_anchor: tuple[float, float, float],
    target_anchor: tuple[float, float, float],
    intent: CoverageIntent,
    rotation_deg: float,
    offset_x: float,
    offset_y: float,
) -> tuple[float, float, int]:
    """Resolve uniform scale for a requested target-area fraction.

    The source and target anchors must belong to their positive-area regions. This
    makes the scale family nested for the fixed orientation/offset case; if that
    precondition is false, returning a plausible number would be unsafe.
    """
    if not isinstance(intent, CoverageIntent):
        raise TypeError("intent must be a CoverageIntent")
    source_anchor = _finite_triplet(source_anchor, "source_anchor")
    target_anchor = _finite_triplet(target_anchor, "target_anchor")
    for name, value in (("rotation_deg", rotation_deg), ("offset_x", offset_x), ("offset_y", offset_y)):
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            raise ValueError(f"{name} must be finite")
    if source_region.is_empty or source_region.area <= _EPS:
        raise ValueError("coverage solving requires a positive-area source geometry")
    if target_region.is_empty or target_region.area <= _EPS:
        raise ValueError("coverage solving requires a positive-area target geometry")
    if not source_region.covers(Point(source_anchor[0], source_anchor[1])):
        raise ValueError("coverage solving requires source_anchor inside source geometry")
    if not target_region.covers(Point(target_anchor[0], target_anchor[1])):
        raise ValueError("coverage solving requires target_anchor inside target geometry")

    desired = intent.target_fraction
    if desired == 0.0:
        scale = 1e-9
        return scale, _coverage_for_scale(
            source_region, target_region, source_anchor, target_anchor,
            scale, rotation_deg, offset_x, offset_y,
        ), 0

    lo, hi = 1e-9, 1.0
    value_hi = _coverage_for_scale(
        source_region, target_region, source_anchor, target_anchor,
        hi, rotation_deg, offset_x, offset_y,
    )
    while value_hi < desired and hi < 1e6:
        hi *= 2.0
        value_hi = _coverage_for_scale(
            source_region, target_region, source_anchor, target_anchor,
            hi, rotation_deg, offset_x, offset_y,
        )
    if value_hi + intent.tolerance < desired:
        raise ValueError("requested coverage is unreachable with the fixed anchor/orientation/offset")

    iterations = 0
    for iterations in range(1, intent.max_iterations + 1):
        mid = (lo + hi) * 0.5
        value = _coverage_for_scale(
            source_region, target_region, source_anchor, target_anchor,
            mid, rotation_deg, offset_x, offset_y,
        )
        if abs(value - desired) <= intent.tolerance:
            return mid, value, iterations
        if value < desired:
            lo = mid
        else:
            hi = mid

    scale = (lo + hi) * 0.5
    return scale, _coverage_for_scale(
        source_region, target_region, source_anchor, target_anchor,
        scale, rotation_deg, offset_x, offset_y,
    ), iterations
