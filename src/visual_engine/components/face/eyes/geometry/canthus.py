from __future__ import annotations

from dataclasses import dataclass
import math


@dataclass(frozen=True, slots=True)
class CanthusEndpoints:
    """Resolved upper/lower margin endpoints for the two ocular corners.

    The endpoint pair is the geometric input to the canthus bridge.  Its vertical
    half-gap is owned by the corresponding inner/outer roundness parameter; no
    shared corner state is used.
    """

    inner_upper: tuple[float, float]
    inner_lower: tuple[float, float]
    outer_upper: tuple[float, float]
    outer_lower: tuple[float, float]


def _endpoint_pair(x: float, radius: float) -> tuple[tuple[float, float], tuple[float, float]]:
    return (x, -radius), (x, radius)


def _numerical_separation(half_w: float, half_h: float) -> float:
    """Return the smallest empirically safe open-eye corner separation.

    This is deliberately a numerical floor, not a hidden aesthetic roundness.
    A focused adversarial sweep found 0.02 * min(half_w, half_h) to be the first
    tested floor that remained topologically safe across the full reconstruction
    matrix (shapes, openings, samples and strong diagonal gaze).  The value is
    therefore a documented robustness constant, not an anatomy claim.
    """
    scale = min(half_w, half_h)
    return max(scale * 0.02, 1e-12)


def _resolve_radius(half_w: float, half_h: float, roundness: float) -> float:
    # Roundness maps directly to a dimensionless geometric half-gap. The clamp
    # keeps extreme authoring inside the eyelid envelope while the numerical floor
    # prevents an open eye from becoming a zero-chord bridge under the current C1
    # representation.
    requested = half_w * roundness
    return min(max(requested, _numerical_separation(half_w, half_h)), half_h * 0.35)


def build_canthus_endpoints(
    half_w: float,
    half_h: float,
    *,
    inner_roundness: float,
    outer_roundness: float,
) -> CanthusEndpoints:
    """Resolve independent inner/outer corner geometry for the open-eye contour.

    Zero authored roundness means the smallest numerically safe corner, not a
    visually significant vertical triangle.  Inner and outer radii are resolved
    independently so changing one corner cannot alter the other.
    """
    if not all(math.isfinite(v) for v in (half_w, half_h, inner_roundness, outer_roundness)):
        raise ValueError("canthus endpoint inputs must be finite")
    if half_w <= 0 or half_h <= 0:
        raise ValueError("canthus endpoint dimensions must be > 0")
    if not 0 <= inner_roundness <= 0.2 or not 0 <= outer_roundness <= 0.2:
        raise ValueError("canthus roundness must be within [0,0.2]")
    inner_r = _resolve_radius(half_w, half_h, inner_roundness)
    outer_r = _resolve_radius(half_w, half_h, outer_roundness)
    iu, il = _endpoint_pair(-half_w, inner_r)
    ou, ol = _endpoint_pair(half_w, outer_r)
    return CanthusEndpoints(iu, il, ou, ol)
