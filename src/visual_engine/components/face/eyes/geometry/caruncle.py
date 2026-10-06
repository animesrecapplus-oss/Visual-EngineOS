from __future__ import annotations

import math

Point = tuple[float, float]


def build_medial_caruncle(
    terminal: Point,
    interior_target: Point,
    *,
    width: float,
    height: float,
    curvature: float,
) -> tuple[Point, ...]:
    """Build a small filled medial caruncle in the local ocular surface.

    The caruncle is intentionally separate from the canthus closure: it is a
    medial ocular-surface detail, not a substitute for the lid terminal.  The
    returned polygon is sampled deterministically and uses curved side control
    points so it cannot collapse into the old vertical bridge/cap artifact.
    """
    if width <= 0 or height <= 0:
        return ()
    vx, vy = interior_target[0] - terminal[0], interior_target[1] - terminal[1]
    length = math.hypot(vx, vy)
    if length <= 1e-15:
        return ()
    ux, uy = vx / length, vy / length
    nx, ny = -uy, ux
    depth = width
    half_h = height * 0.5
    curvature = min(1.0, max(0.0, curvature))

    # Tip remains close to the canthal terminal; the broad base sits inside the
    # sclera.  The two cubic side arcs are sampled into one closed polygon.
    tip = (terminal[0] + ux * depth * 0.10, terminal[1] + uy * depth * 0.10)
    upper = (terminal[0] + ux * depth, terminal[1] + uy * depth + ny * half_h)
    lower = (terminal[0] + ux * depth, terminal[1] + uy * depth - ny * half_h)
    bulge = depth * (0.10 + 0.22 * curvature)
    c1 = (tip[0] + ux * depth * 0.38 + nx * half_h * 0.18,
          tip[1] + uy * depth * 0.38 + ny * half_h * 0.18)
    c2 = (upper[0] - ux * depth * 0.22 + nx * bulge,
          upper[1] - uy * depth * 0.22 + ny * bulge)
    c3 = (lower[0] - ux * depth * 0.22 - nx * bulge,
          lower[1] - uy * depth * 0.22 - ny * bulge)
    c4 = (tip[0] + ux * depth * 0.38 - nx * half_h * 0.18,
          tip[1] + uy * depth * 0.38 - ny * half_h * 0.18)

    def cubic(a, b, c, d, samples=9):
        out = []
        for i in range(samples):
            t = i / (samples - 1)
            u = 1.0 - t
            out.append((
                u**3*a[0] + 3*u*u*t*b[0] + 3*u*t*t*c[0] + t**3*d[0],
                u**3*a[1] + 3*u*u*t*b[1] + 3*u*t*t*c[1] + t**3*d[1],
            ))
        return out

    left = cubic(tip, c1, c2, upper)
    right = cubic(upper, c3, c4, lower)
    return tuple(left + right[1:] + [tip])
