from __future__ import annotations

import math
from dataclasses import replace

from ..gaze.solver import Gaze

Point = tuple[float, float]


def rotate_point(point: Point, degrees: float) -> Point:
    """Rotate a point in the canonical ocular frame."""
    angle = math.radians(degrees)
    c, s = math.cos(angle), math.sin(angle)
    x, y = point
    return c * x - s * y, s * x + c * y


def world_relative_to_local(point: Point, degrees: float) -> Point:
    """Apply the inverse eye-parent rotation to a world-relative point."""
    return rotate_point(point, -degrees)


def local_to_world_relative(point: Point, degrees: float) -> Point:
    """Apply the eye-parent rotation to a canonical local point."""
    return rotate_point(point, degrees)


def gaze_to_local(gaze: Gaze, center: Point, rotation_deg: float) -> Gaze:
    """Resolve scene-space target/offsets in the eye-local frame.

    Named gaze directions remain semantic local directions; only explicit scene
    coordinates need the inverse parent rotation.
    """
    ox, oy = world_relative_to_local((gaze.x, gaze.y), rotation_deg)
    target = None
    if gaze.target is not None:
        target = world_relative_to_local(
            (gaze.target[0] - center[0], gaze.target[1] - center[1]), rotation_deg
        )
    return replace(gaze, x=ox, y=oy, target=target)
