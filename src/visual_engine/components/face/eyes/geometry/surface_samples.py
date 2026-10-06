from __future__ import annotations

import math
from .projection3d import Camera3D, Point2, project_point
from typing import Protocol

Vec3 = tuple[float, float, float]

class SurfaceAttachment(Protocol):
    center: Vec3
    normal: Vec3
    tangent_x: Vec3
    tangent_y: Vec3


def project_spherical_patch_samples(attachment: SurfaceAttachment, patch_radius: float, globe_radius: float, camera: Camera3D, samples: int = 96) -> tuple[tuple[Point2, ...], tuple[Vec3, ...]]:
    """Return the projected and 3D samples of one spherical child surface."""
    if patch_radius <= 0 or globe_radius <= 0 or patch_radius >= globe_radius:
        raise ValueError("spherical patch radius must be smaller than globe radius")
    if samples < 24:
        raise ValueError("spherical patch requires at least 24 samples")
    theta = math.asin(min(0.999999, patch_radius / globe_radius))
    origin = tuple(attachment.center[i] - attachment.normal[i] * globe_radius for i in range(3))
    points3 = []
    for i in range(samples):
        t = 2.0 * math.pi * i / samples
        tangent = tuple(
            attachment.tangent_x[j] * math.cos(t) + attachment.tangent_y[j] * math.sin(t)
            for j in range(3)
        )
        radial = tuple(
            attachment.normal[j] * math.cos(theta) + tangent[j] * math.sin(theta)
            for j in range(3)
        )
        points3.append(tuple(origin[j] + radial[j] * globe_radius for j in range(3)))
    return tuple(project_point(p, camera) for p in points3), tuple(points3)
