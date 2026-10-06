from __future__ import annotations

"""Renderer-neutral measurements of the ocular envelope.

The metric layer deliberately measures the already-resolved lid geometry instead of
reconstructing it.  This prevents a second geometry implementation from silently
becoming the reference model.  All ratios are expressed in the local eye frame
whose longitudinal axis is the inner→outer canthus vector.
"""

import math
from dataclasses import dataclass

Point = tuple[float, float]
_EPS = 1e-15


@dataclass(frozen=True, slots=True)
class EnvelopeMetrics:
    """Dimensionless envelope measurements plus the two physical eye dimensions.

    ``t`` coordinates refer to the existing sampled parameter order: 0 is inner
    canthus and 1 is outer canthus.  ``u``/``v`` are invariant local coordinates:
    ``u`` runs along the canthus axis and ``v`` is its left-normal.  For the normal
    eye orientation, upper-lid points have smaller ``v`` than lower-lid points.
    """

    valid: bool
    width: float
    height: float
    aspect_ratio: float | None
    opening_max: float
    opening_ratio: float
    opening_area: float
    opening_area_ratio: float
    opening_balance: float
    min_gap: float
    t_open: float | None
    u_open: float | None
    upper_apex_t: float
    upper_apex_u: float
    upper_apex_v: float
    lower_apex_t: float
    lower_apex_u: float
    lower_apex_v: float
    upper_depth: float
    lower_depth: float
    lid_depth_balance: float
    axis_angle_rad: float


def _finite_point(p: Point) -> bool:
    return math.isfinite(p[0]) and math.isfinite(p[1])


def _local_frame(inner: Point, outer: Point) -> tuple[float, Point, Point, Point]:
    dx, dy = outer[0] - inner[0], outer[1] - inner[1]
    width = math.hypot(dx, dy)
    if not math.isfinite(width) or width <= _EPS:
        raise ValueError("inner and outer canthi must define a finite non-zero width")
    e = (dx / width, dy / width)
    n = (-e[1], e[0])
    midpoint = ((inner[0] + outer[0]) * 0.5, (inner[1] + outer[1]) * 0.5)
    return width, e, n, midpoint


def _uv(point: Point, inner: Point, e: Point, n: Point, width: float) -> Point:
    rx, ry = point[0] - inner[0], point[1] - inner[1]
    return ((rx * e[0] + ry * e[1]) / width,
            (rx * n[0] + ry * n[1]) / width)


def _first_extreme(values: tuple[float, ...], *, minimum: bool) -> int:
    target = min(values) if minimum else max(values)
    return values.index(target)


def _trapezoid(values: tuple[float, ...]) -> float:
    if len(values) < 2:
        return 0.0
    step = 1.0 / (len(values) - 1)
    return step * (0.5 * values[0] + sum(values[1:-1]) + 0.5 * values[-1])


def _integral_half(values: tuple[float, ...], start: float, end: float) -> float:
    """Integrate a piecewise-linear gap on an arbitrary t interval.

    The sampled lid curves already share the same parameter count.  Splitting
    each segment at the requested boundary avoids the common half-integral error
    caused by assuming that the sample count is even.
    """
    if end <= start:
        return 0.0
    n = len(values)
    total = 0.0
    for i in range(n - 1):
        a, b = i / (n - 1), (i + 1) / (n - 1)
        left, right = max(a, start), min(b, end)
        if right <= left:
            continue
        span = b - a
        va = values[i] + (values[i + 1] - values[i]) * ((left - a) / span)
        vb = values[i] + (values[i + 1] - values[i]) * ((right - a) / span)
        total += 0.5 * (va + vb) * (right - left)
    return total


def measure_envelope(
    upper: tuple[Point, ...],
    lower: tuple[Point, ...],
    inner: Point,
    outer: Point,
    *,
    tolerance: float | None = None,
) -> EnvelopeMetrics:
    """Measure an eye envelope from final, paired upper/lower lid samples.

    Contract assumptions are explicit: both curves are ordered inner→outer and
    have equal sample counts.  The function does not alter geometry and reports
    ``valid=False`` instead of repairing malformed input.
    """
    if len(upper) < 2 or len(lower) < 2 or len(upper) != len(lower):
        raise ValueError("upper/lower envelope samples must have equal length >= 2")
    points = (*upper, *lower, inner, outer)
    if not all(_finite_point(p) for p in points):
        raise ValueError("envelope points must be finite")
    width, e, n, midpoint = _local_frame(inner, outer)
    upper_uv = tuple(_uv(p, inner, e, n, width) for p in upper)
    lower_uv = tuple(_uv(p, inner, e, n, width) for p in lower)

    # The semantic frame is anchored to the upper-lid canthi. The lower lid is
    # allowed a small medial/lateral inset at each corner; that offset is part of
    # the canthus geometry, not evidence that the envelope frame is wrong.
    endpoint_error = max(abs(upper_uv[0][0]), abs(upper_uv[-1][0] - 1.0))
    scale_tol = max(width * 1e-9, 1e-15) if tolerance is None else tolerance
    if scale_tol < 0 or not math.isfinite(scale_tol):
        raise ValueError("envelope tolerance must be finite and >= 0")
    normalized_tol = scale_tol / width

    all_v = tuple(v for _, v in (*upper_uv, *lower_uv))
    height = (max(all_v) - min(all_v)) * width
    aspect_ratio = width / height if height > normalized_tol * width else None

    gaps = tuple(lv - uv for (_, uv), (_, lv) in zip(upper_uv, lower_uv))
    min_gap = min(gaps) * width
    opening_max = max(0.0, max(gaps) * width)
    opening_ratio = opening_max / width
    opening_area = max(0.0, _trapezoid(gaps) * width)
    opening_area_ratio = opening_area / width
    left_area = max(0.0, _integral_half(gaps, 0.0, 0.5) * width)
    right_area = max(0.0, _integral_half(gaps, 0.5, 1.0) * width)
    area_sum = left_area + right_area
    opening_balance = (right_area - left_area) / area_sum if area_sum > _EPS * width else 0.0

    max_gap = max(gaps)
    # Floating-point rotation can make a mathematically tied pair differ by a few
    # ulps. A tiny relative plateau tolerance prevents t_open from flipping from
    # 0.484 to 0.516 solely because the eye was rotated. It is not a visual fudge:
    # it only resolves numerically tied discrete samples.
    tie_tol = max(1e-12, abs(max_gap) * 1e-10)
    max_indices = tuple(i for i, value in enumerate(gaps) if max_gap - value <= tie_tol)
    max_gap_index = max_indices[0]
    t_open = (
        sum(i / (len(gaps) - 1) for i in max_indices) / len(max_indices)
        if opening_max > normalized_tol * width else None
    )
    u_open = (
        sum((upper_uv[i][0] + lower_uv[i][0]) * 0.5 for i in max_indices) / len(max_indices)
        if t_open is not None else None
    )

    upper_v = tuple(v for _, v in upper_uv)
    lower_v = tuple(v for _, v in lower_uv)
    upper_index = _first_extreme(upper_v, minimum=True)
    lower_index = _first_extreme(lower_v, minimum=False)
    upper_apex_t = upper_index / (len(upper) - 1)
    lower_apex_t = lower_index / (len(lower) - 1)
    upper_apex_u, upper_apex_v = upper_uv[upper_index]
    lower_apex_u, lower_apex_v = lower_uv[lower_index]

    # The midpoint of the semantic canthi is the origin of the local normal axis,
    # so v=0 is the exact anatomical midline even when the eye is rotated.
    mid_v = 0.0
    upper_depth = max(0.0, mid_v - min(upper_v)) * width
    lower_depth = max(0.0, max(lower_v) - mid_v) * width
    depth_sum = upper_depth + lower_depth
    lid_depth_balance = (upper_depth - lower_depth) / depth_sum if depth_sum > _EPS * width else 0.0

    valid = (
        endpoint_error <= normalized_tol
        and min_gap >= -scale_tol
        and all(math.isfinite(value) for value in (
            width, height, opening_max, opening_area, opening_balance,
            upper_depth, lower_depth, lid_depth_balance,
        ))
    )
    return EnvelopeMetrics(
        valid=valid,
        width=width,
        height=height,
        aspect_ratio=aspect_ratio,
        opening_max=opening_max,
        opening_ratio=opening_ratio,
        opening_area=opening_area,
        opening_area_ratio=opening_area_ratio,
        opening_balance=opening_balance,
        min_gap=min_gap,
        t_open=t_open,
        u_open=u_open,
        upper_apex_t=upper_apex_t,
        upper_apex_u=upper_apex_u,
        upper_apex_v=upper_apex_v,
        lower_apex_t=lower_apex_t,
        lower_apex_u=lower_apex_u,
        lower_apex_v=lower_apex_v,
        upper_depth=upper_depth,
        lower_depth=lower_depth,
        lid_depth_balance=lid_depth_balance,
        axis_angle_rad=math.atan2(e[1], e[0]),
    )
