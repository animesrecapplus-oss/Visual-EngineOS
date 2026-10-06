from __future__ import annotations

import math

def _nearest_radial_limit(x: float, y: float, points: tuple[tuple[float, float], ...]) -> float:
    # Conservative radial bound: minimum radius of the sampled contour in the requested direction.
    angle = math.atan2(y, x)
    radii: list[float] = []
    for px, py in points:
        a = math.atan2(py, px)
        da = abs((a - angle + math.pi) % (2 * math.pi) - math.pi)
        if da < math.pi / 8:
            radii.append(math.hypot(px, py))
    if not radii:
        radii = [math.hypot(px, py) for px, py in points]
    return min(radii)


def _clamp_to_iris(x: float, y: float, iris_center: tuple[float, float], rx: float, ry: float, margin: float) -> tuple[float, float]:
    """Conservatively keep a pupil centre inside the iris ellipse."""
    cx, cy = iris_center
    ax = max(rx - margin, 1e-9)
    ay = max(ry - margin, 1e-9)
    dx, dy = x - cx, y - cy
    q = (dx / ax) ** 2 + (dy / ay) ** 2
    if q <= 1.0:
        return x, y
    scale = 1.0 / math.sqrt(q)
    return cx + dx * scale, cy + dy * scale


def _clamp_to_sampled_contour(x: float, y: float, points: tuple[tuple[float, float], ...], margin: float) -> tuple[float, float]:
    r = math.hypot(x, y)
    if r <= 1e-12:
        return 0.0, 0.0
    limit = max(_nearest_radial_limit(x, y, points) - margin, 1e-9)
    if r <= limit:
        return x, y
    s = limit / r
    return x * s, y * s
