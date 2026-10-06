from __future__ import annotations

import math
from dataclasses import dataclass

Point = tuple[float, float]
Cubic = tuple[Point, Point, Point, Point]


@dataclass(frozen=True, slots=True)
class ContourContinuityReport:
    """Numerical evidence for a closed ocular contour's C1 canthus joins.

    The eye geometry stores sampled upper/lower lid curves. Rendering historically
    interpolated those samples with the same endpoint tangent convention as
    ``_smooth_open_path``.  This contract makes that convention explicit: the
    bridge derivative must equal the derivative of the adjacent lid curve at
    each canthus.  Equality of vectors is stronger than merely requiring a
    visually collinear (G1) join.
    """

    valid: bool
    outer_start_error: float
    outer_end_error: float
    inner_start_error: float
    inner_end_error: float
    min_tangent_norm: float
    max_error: float
    c1_bridges_present: bool = True

    @property
    def tangent_continuous(self) -> bool:
        return self.valid and self.c1_bridges_present


def _sub(a: Point, b: Point) -> Point:
    return a[0] - b[0], a[1] - b[1]


def _add(a: Point, b: Point) -> Point:
    return a[0] + b[0], a[1] + b[1]


def _scale(a: Point, value: float) -> Point:
    return a[0] * value, a[1] * value


def _norm(a: Point) -> float:
    return math.hypot(a[0], a[1])


def _finite_point(point: Point) -> bool:
    return math.isfinite(point[0]) and math.isfinite(point[1])


def _endpoint_tangent(points: tuple[Point, ...], *, at_end: bool) -> Point:
    """Match the renderer's endpoint derivative convention exactly.

    For a sampled open curve the cubic interpolator uses the first/last two
    interior samples as its endpoint tangent. The factor 1/2 is its actual
    derivative scale and is retained so the bridge is C1, not merely G1.
    """
    if len(points) < 3:
        raise ValueError("at least three samples are required for endpoint tangents")
    if at_end:
        return _scale(_sub(points[-1], points[-3]), 0.5)
    return _scale(_sub(points[2], points[0]), 0.5)


def _bridge(start: Point, start_tangent: Point, end: Point, end_tangent: Point) -> Cubic:
    """Construct one cubic bridge whose endpoint derivatives match its neighbours."""
    return (
        start,
        _add(start, _scale(start_tangent, 1.0 / 3.0)),
        _sub(end, _scale(end_tangent, 1.0 / 3.0)),
        end,
    )


def build_canthus_bridges(
    upper: tuple[Point, ...],
    lower: tuple[Point, ...],
) -> tuple[Cubic, Cubic]:
    """Return ``(outer, inner)`` cubic bridges for the closed eye contour.

    Traversal is upper inner→outer, outer bridge outer→lower outer, lower
    outer→inner, then inner bridge inner→upper inner. The bridge construction
    is purely geometric and therefore remains renderer-independent.
    """
    if len(upper) < 3 or len(lower) < 3:
        raise ValueError("canthus continuity requires at least three lid samples")
    outer = _bridge(
        upper[-1],
        _endpoint_tangent(upper, at_end=True),
        lower[-1],
        _endpoint_tangent(tuple(reversed(lower)), at_end=False),
    )
    inner = _bridge(
        lower[0],
        _endpoint_tangent(tuple(reversed(lower)), at_end=True),
        upper[0],
        _endpoint_tangent(upper, at_end=False),
    )
    return outer, inner


def _cubic_derivative_start(curve: Cubic) -> Point:
    return _scale(_sub(curve[1], curve[0]), 3.0)


def _cubic_derivative_end(curve: Cubic) -> Point:
    return _scale(_sub(curve[3], curve[2]), 3.0)


def assess_contour_continuity(
    upper: tuple[Point, ...],
    lower: tuple[Point, ...],
    outer_bridge: Cubic | tuple[()] | tuple,
    inner_bridge: Cubic | tuple[()] | tuple,
    *,
    tolerance: float | None = None,
    tangent_epsilon: float | None = None,
) -> ContourContinuityReport:
    """Check terminal attachment and C1 equality where a bridge is explicitly present.

    V1.7 shared-point terminals intentionally have no bridge and therefore do not
    claim C1 continuity across the semantic corner.
    """
    lid_points = [point for curve in (upper, lower) for point in curve]
    bridge_points = [point for curve in (outer_bridge, inner_bridge) for point in curve]
    finite = all(_finite_point(point) for point in (*lid_points, *bridge_points))
    if not finite or len(upper) < 3 or len(lower) < 3:
        return ContourContinuityReport(False, math.inf, math.inf, math.inf, math.inf, 0.0, math.inf, False)

    upper_end = _endpoint_tangent(upper, at_end=True)
    lower_outer = _endpoint_tangent(tuple(reversed(lower)), at_end=False)
    lower_inner = _endpoint_tangent(tuple(reversed(lower)), at_end=True)
    upper_start = _endpoint_tangent(upper, at_end=False)

    bridges_present = len(outer_bridge) == 4 and len(inner_bridge) == 4
    def bridge_errors(bridge, start_tangent, end_tangent, start_point, end_point):
        if len(bridge) == 4:
            return (
                _norm(_sub(_cubic_derivative_start(bridge), start_tangent)),
                _norm(_sub(_cubic_derivative_end(bridge), end_tangent)),
                _norm(_sub(bridge[0], start_point)),
                _norm(_sub(bridge[3], end_point)),
            )
        # Shared-point terminal: both lids must terminate at the same point.
        gap = _norm(_sub(start_point, end_point))
        return (0.0, 0.0, gap, gap)

    outer_errors = bridge_errors(outer_bridge, upper_end, lower_outer, upper[-1], lower[-1])
    inner_errors = bridge_errors(inner_bridge, lower_inner, upper_start, lower[0], upper[0])
    errors = outer_errors[:2] + inner_errors[:2]
    attachment_errors = outer_errors[2:] + inner_errors[2:]
    tangent_norms = tuple(_norm(t) for t in (upper_end, lower_outer, lower_inner, upper_start))
    min_tangent = min(tangent_norms)
    bridge_scales = tuple(
        _norm(_sub(curve[1], curve[0])) for curve in (outer_bridge, inner_bridge) if len(curve) == 4
    )
    scale = max(max(tangent_norms), *bridge_scales, 1e-15)
    effective_tolerance = max(1e-9 * scale, 1e-15) if tolerance is None else tolerance
    effective_tangent_epsilon = (1e-12 * scale) if tangent_epsilon is None else tangent_epsilon
    if effective_tolerance < 0 or not math.isfinite(effective_tolerance):
        raise ValueError("continuity tolerance must be finite and >= 0")
    if effective_tangent_epsilon < 0 or not math.isfinite(effective_tangent_epsilon):
        raise ValueError("tangent epsilon must be finite and >= 0")
    max_error = max((*errors, *attachment_errors))
    valid = min_tangent > effective_tangent_epsilon and max_error <= effective_tolerance
    return ContourContinuityReport(
        valid=valid,
        outer_start_error=errors[0],
        outer_end_error=errors[1],
        inner_start_error=errors[2],
        inner_end_error=errors[3],
        min_tangent_norm=min_tangent,
        max_error=max_error,
        c1_bridges_present=bridges_present,
    )


def sample_cubic(curve: Cubic, samples: int = 8) -> tuple[Point, ...]:
    """Sample a bridge for topology/safety checks without owning rendering."""
    if samples < 2:
        raise ValueError("bridge sample count must be >= 2")
    out: list[Point] = []
    for i in range(samples):
        u = i / (samples - 1)
        v = 1.0 - u
        out.append((
            v**3 * curve[0][0] + 3*v*v*u*curve[1][0] + 3*v*u*u*curve[2][0] + u**3*curve[3][0],
            v**3 * curve[0][1] + 3*v*v*u*curve[1][1] + 3*v*u*u*curve[2][1] + u**3*curve[3][1],
        ))
    return tuple(out)


def closed_contour_samples(
    upper: tuple[Point, ...],
    lower: tuple[Point, ...],
    outer_bridge: Cubic | tuple[()] | tuple,
    inner_bridge: Cubic | tuple[()] | tuple,
    *,
    bridge_samples: int = 8,
) -> tuple[Point, ...]:
    """Compose a deterministic sampled closed contour for topology checks."""
    outer = sample_cubic(outer_bridge, bridge_samples)[1:-1] if len(outer_bridge) == 4 else ()
    inner = sample_cubic(inner_bridge, bridge_samples)[1:-1] if len(inner_bridge) == 4 else ()
    return tuple(upper) + outer + tuple(reversed(lower)) + inner
