from __future__ import annotations

import math

from ..contracts.types import EyeShape

def _shape_factors(shape: EyeShape) -> tuple[float, float]:
    # `round` is a semantic promise: with the default width/height it must
    # produce a circular aperture, not an ellipse that merely looks round-ish.
    # `ellipse` is the explicit escape hatch when the author wants an ellipse.
    return {
        "almond": (1.00, 1.00),
        "round": (1.00, 1.8181818181818181),
        "large_round": (1.20, 2.1818181818181817),
        "ellipse": (1.00, 1.00),
        "narrow": (1.08, 0.55),
        "droopy": (1.05, 0.88),
        "sharp": (1.08, 0.82),
        "upturned": (1.05, 0.95),
        "downturned": (1.05, 0.95),
    }[shape]


def _rotate(x: float, y: float, deg: float) -> tuple[float, float]:
    r = math.radians(deg)
    c, s = math.cos(r), math.sin(r)
    return c * x - s * y, s * x + c * y


def _clamp_point_to_eye(x: float, y: float, half_w: float, half_h: float, margin_x: float = 0.0, margin_y: float = 0.0) -> tuple[float, float]:
    hw, hh = max(half_w - margin_x, 1e-9), max(half_h - margin_y, 1e-9)
    q = (x / hw) ** 2 + (y / hh) ** 2
    if q <= 1.0:
        return x, y
    s = 1.0 / math.sqrt(q)
    return x * s, y * s
