from __future__ import annotations

from dataclasses import dataclass
import math

from .view_axis import Vec3, OcularBasis3D, OcularPose3D, compose_ocular_basis

Point2 = tuple[float, float]


@dataclass(frozen=True, slots=True)
class Camera3D:
    """Minimal pinhole camera used only when perspective is explicitly requested."""

    position: Vec3 = (0.0, 0.0, 10.0)
    focal_length: float = 10.0
    orthographic: bool = True

    def __post_init__(self) -> None:
        if not all(math.isfinite(v) for v in self.position + (self.focal_length,)):
            raise ValueError("camera values must be finite")
        if self.focal_length <= 0:
            raise ValueError("focal_length must be > 0")


def _project_point(point: Vec3, camera: Camera3D) -> Point2:
    x, y, z = point
    cx, cy, cz = camera.position
    dx, dy, dz = x - cx, y - cy, z - cz
    if camera.orthographic:
        return dx, -dy
    depth = cz - z
    if depth <= 1e-9:
        raise ValueError("point is on or behind the perspective camera plane")
    scale = camera.focal_length / depth
    return dx * scale, -dy * scale


def project_point(point: Vec3, camera: Camera3D = Camera3D()) -> Point2:
    return _project_point(point, camera)


def project_sphere_silhouette(center: Vec3, radius: float, camera: Camera3D = Camera3D(), *, samples: int = 128) -> tuple[Point2, ...]:
    """Project a sphere silhouette.

    Under orthographic projection a sphere remains circular; its orientation does
    not change that fact. The aperture, not an artificial ellipse, is responsible
    for the visible eye-shape reduction. Perspective uses the exact tangent-cone
    silhouette construction around the camera, avoiding a misleading squashed
    circle approximation.
    """
    if radius <= 0 or not math.isfinite(radius):
        raise ValueError("sphere radius must be finite and > 0")
    if samples < 32:
        raise ValueError("sphere silhouette requires at least 32 samples")
    if camera.orthographic:
        # Camera looks along -Z from +Z; the screen basis is +X/-Y.
        return tuple((center[0] + radius * math.cos(2 * math.pi * i / samples),
                      -(center[1] + radius * math.sin(2 * math.pi * i / samples))) for i in range(samples))
    vx, vy, vz = (camera.position[i] - center[i] for i in range(3))
    d = math.sqrt(vx * vx + vy * vy + vz * vz)
    if d <= radius:
        raise ValueError("perspective camera must be outside the sphere")
    view = (vx / d, vy / d, vz / d)
    helper = (0.0, 1.0, 0.0) if abs(view[1]) < 0.9 else (1.0, 0.0, 0.0)
    u = _unit_cross(helper, view)
    v = _cross(view, u)
    alpha = math.asin(radius / d)
    ring_center = (center[0] + view[0] * radius * radius / d,
                   center[1] + view[1] * radius * radius / d,
                   center[2] + view[2] * radius * radius / d)
    ring_radius = radius * math.sqrt(max(0.0, 1.0 - (radius / d) ** 2))
    return tuple(_project_point((ring_center[0] + ring_radius * (u[0] * math.cos(t) + v[0] * math.sin(t)),
                                 ring_center[1] + ring_radius * (u[1] * math.cos(t) + v[1] * math.sin(t)),
                                 ring_center[2] + ring_radius * (u[2] * math.cos(t) + v[2] * math.sin(t))), camera)
                 for t in (2 * math.pi * i / samples for i in range(samples)))


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _unit_cross(a: Vec3, b: Vec3) -> Vec3:
    c = _cross(a, b)
    n = math.sqrt(sum(v * v for v in c))
    if n <= 1e-12:
        raise ValueError("camera basis construction is degenerate")
    return tuple(v / n for v in c)


def project_oriented_circle(center: Vec3, normal: Vec3, radius: float, camera: Camera3D = Camera3D(), *, samples: int = 96) -> tuple[Point2, ...]:
    """Project a circle whose plane normal is ``normal``.

    This is the geometric source of the apparent iris ellipse. No screen-space
    cosine scaling is inserted; the ellipse emerges from projection of 3D points.
    """
    if radius <= 0 or samples < 24:
        raise ValueError("invalid circle radius/sample count")
    n = _unit(normal)
    helper = (1.0, 0.0, 0.0) if abs(n[0]) < 0.9 else (0.0, 1.0, 0.0)
    u = _unit_cross(n, helper)
    v = _cross(n, u)
    return tuple(project_point((center[0] + radius * (u[0] * math.cos(t) + v[0] * math.sin(t)),
                                center[1] + radius * (u[1] * math.cos(t) + v[1] * math.sin(t)),
                                center[2] + radius * (u[2] * math.cos(t) + v[2] * math.sin(t))), camera)
                 for t in (2 * math.pi * i / samples for i in range(samples)))


def _unit(v: Vec3) -> Vec3:
    n = math.sqrt(sum(x * x for x in v))
    if n <= 1e-12 or not math.isfinite(n):
        raise ValueError("vector must be finite and non-zero")
    return tuple(x / n for x in v)


def projected_ellipse_rotation(points: tuple[Point2, ...]) -> float:
    """Estimate the principal image-plane axis of a dense projected circle."""
    if len(points) < 3:
        return 0.0
    cx = sum(x for x, _ in points) / len(points); cy = sum(y for _, y in points) / len(points)
    qxx = sum((x-cx)*(x-cx) for x, _ in points); qxy = sum((x-cx)*(y-cy) for x, y in points)
    qyy = sum((y-cy)*(y-cy) for _, y in points)
    return math.degrees(0.5 * math.atan2(2.0*qxy, qxx-qyy))
