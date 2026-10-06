from __future__ import annotations

import math


def _orientation(a, b, c) -> float:
    return (b[0] - a[0]) * (c[1] - a[1]) - (b[1] - a[1]) * (c[0] - a[0])


def _on_segment(a, b, p, eps: float) -> bool:
    return (
        min(a[0], b[0]) - eps <= p[0] <= max(a[0], b[0]) + eps
        and min(a[1], b[1]) - eps <= p[1] <= max(a[1], b[1]) + eps
    )


def _segments_intersect(a, b, c, d, eps: float) -> bool:
    o1, o2 = _orientation(a, b, c), _orientation(a, b, d)
    o3, o4 = _orientation(c, d, a), _orientation(c, d, b)
    if (o1 > eps and o2 < -eps or o1 < -eps and o2 > eps) and (o3 > eps and o4 < -eps or o3 < -eps and o4 > eps):
        return True
    return (
        abs(o1) <= eps and _on_segment(a, b, c, eps)
        or abs(o2) <= eps and _on_segment(a, b, d, eps)
        or abs(o3) <= eps and _on_segment(c, d, a, eps)
        or abs(o4) <= eps and _on_segment(c, d, b, eps)
    )


def has_self_intersection(points: tuple[tuple[float, float], ...], *, epsilon: float | None = None) -> bool:
    """Return whether a closed polyline contains a non-adjacent crossing.

    The default tolerance is scale-relative. A fixed absolute epsilon would turn
    legitimate joins into false positives when ``opening`` approaches zero or
    when the same geometry is authored at a much smaller physical scale.
    Explicit ``epsilon`` remains available for callers that require a fixed
    numerical tolerance.
    """
    if len(points) < 4:
        return False
    if epsilon is None:
        xs = [x for x, _ in points]
        ys = [y for _, y in points]
        scale = max(max(xs) - min(xs), max(ys) - min(ys), 1e-15)
        epsilon = 1e-12 * scale
    if epsilon < 0 or not math.isfinite(epsilon):
        raise ValueError("epsilon must be finite and >= 0")
    n = len(points)
    for i in range(n):
        a, b = points[i], points[(i + 1) % n]
        for j in range(i + 1, n):
            if j in {i - 1, i, i + 1} or (i == 0 and j == n - 1):
                continue
            c, d = points[j], points[(j + 1) % n]
            # Adjacent segments and the explicit closed-loop endpoint joins are
            # allowed to meet. Only a crossing away from a shared endpoint is
            # a morphology self-intersection.
            if any(
                math.hypot(p[0] - q[0], p[1] - q[1]) <= epsilon
                for p in (a, b) for q in (c, d)
            ):
                continue
            if _segments_intersect(a, b, c, d, epsilon):
                return True
    return False


def assert_finite_contour(points: tuple[tuple[float, float], ...]) -> None:
    if not points or any(not (math.isfinite(x) and math.isfinite(y)) for x, y in points):
        raise ValueError("eye contour must contain finite points")
