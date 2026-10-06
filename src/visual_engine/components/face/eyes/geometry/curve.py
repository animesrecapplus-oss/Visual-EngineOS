from __future__ import annotations

import math

def _bezier(p0, p1, p2, p3, u: float) -> tuple[float, float]:
    v = 1.0 - u
    return (
        v*v*v*p0[0] + 3*v*v*u*p1[0] + 3*v*u*u*p2[0] + u*u*u*p3[0],
        v*v*v*p0[1] + 3*v*v*u*p1[1] + 3*v*u*u*p2[1] + u*u*u*p3[1],
    )
def _sample_subcurve(points: tuple[tuple[float, float], ...], fraction: float, *, from_center: bool = False) -> tuple[tuple[float, float], ...]:
    """Return a centered subcurve while preserving endpoint order."""
    if len(points) < 2:
        return points
    f = min(1.0, max(0.05, fraction))
    span = (len(points) - 1) * f
    start = (len(points) - 1 - span) * 0.5
    end = start + span
    n = max(4, int(round(len(points) * f)))
    out = []
    for i in range(n):
        t = start + (end-start) * (i / max(n-1,1))
        j = min(len(points)-2, max(0, int(math.floor(t))))
        u = t-j
        x = points[j][0] * (1-u) + points[j+1][0] * u
        y = points[j][1] * (1-u) + points[j+1][1] * u
        out.append((x,y))
    return tuple(out)


def _offset_curve(points: tuple[tuple[float, float], ...], offset: float, direction: float) -> tuple[tuple[float, float], ...]:
    """Offset a sampled lid curve by its local y direction in eye coordinates.

    The eye model is 2D and intentionally uses a stable vertical offset here;
    the crease follows the lid curvature through the sampled y values.
    """
    return tuple((x, y + direction * offset) for x, y in points)
