from __future__ import annotations

from dataclasses import dataclass
import math

from .spherical_assembly import Vec3
from .view_axis import OcularBasis3D

Point2 = tuple[float, float]


@dataclass(frozen=True, slots=True)
class SurfaceTrace3D:
    """A lid/canthus trace lifted onto the globe/orbital surface."""

    points: tuple[Vec3, ...]
    surface_kind: str
    front_facing_fraction: float


@dataclass(frozen=True, slots=True)
class EyelidSurfaceCoupling:
    """V1.14 bridge between 2D aperture morphology and 3D ocular depth."""

    upper: SurfaceTrace3D
    lower: SurfaceTrace3D
    inner_canthus: Vec3
    outer_canthus: Vec3
    near_canthus: str
    far_canthus: str
    near_canthus_depth: float
    far_canthus_depth: float
    caruncle: SurfaceTrace3D | None = None
    epicanthus: SurfaceTrace3D | None = None
    self_intersections_2d: int = 0
    # V1.18 projected lid traces: face canthi stay fixed while interior lid
    # samples slide over the rotating globe surface.
    projected_upper: tuple[Point2, ...] = ()
    projected_lower: tuple[Point2, ...] = ()


def _dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _norm(v: Vec3) -> float:
    return math.sqrt(_dot(v, v))


def _surface_point(
    point: Point2,
    center: Vec3,
    radius: float,
    basis: OcularBasis3D,
    *,
    orbital_x: float,
    orbital_y: float,
    orbital_z: float,
) -> tuple[Vec3, str]:
    """Lift a screen-space lid point by intersecting its camera ray with a surface.

    Orthographic screen coordinates determine world X/Y directly. The missing Z
    coordinate is solved from the actual sphere first; only points outside that
    footprint fall back to the larger orbital shell. This avoids the V1.13 error
    of treating screen X/Y as ocular-local coordinates after yaw/pitch.
    """
    x = point[0] - center[0]
    y = -(point[1] - center[1])
    sphere_rem = radius * radius - x * x - y * y
    if sphere_rem > 1e-12:
        z = math.sqrt(sphere_rem)
        kind = "globe"
    else:
        nx = x / max(orbital_x, 1e-12)
        ny = y / max(orbital_y, 1e-12)
        rem = 1.0 - nx * nx - ny * ny
        if rem <= 1e-12:
            # The aperture can extend beyond even the orbital shell. Keep the
            # point on a finite front skin instead of manufacturing a negative Z.
            z = 0.0
        else:
            z = orbital_z * math.sqrt(rem)
        kind = "orbital_shell"
    return (center[0] + x, center[1] + y, center[2] + z), kind


def _lift_trace(points: tuple[Point2, ...], center: Vec3, radius: float, basis: OcularBasis3D) -> SurfaceTrace3D:
    orbital_x = max(radius * 1.05, max((abs(p[0] - center[0]) for p in points), default=radius))
    orbital_y = max(radius * 0.72, max((abs(p[1] - center[1]) for p in points), default=radius * .72))
    orbital_z = radius * 1.03
    lifted = []
    kinds = set()
    front = 0
    for point in points:
        p3, kind = _surface_point(point, center, radius, basis, orbital_x=orbital_x, orbital_y=orbital_y, orbital_z=orbital_z)
        lifted.append(p3)
        kinds.add(kind)
        if p3[2] >= center[2]:
            front += 1
    fraction = front / len(lifted) if lifted else 0.0
    kind = "globe+orbital_shell" if len(kinds) > 1 else (next(iter(kinds)) if kinds else "empty")
    return SurfaceTrace3D(tuple(lifted), kind, fraction)


def _depth(point: Vec3, center: Vec3, camera_forward: Vec3) -> float:
    return _dot((point[0] - center[0], point[1] - center[1], point[2] - center[2]), camera_forward)


def couple_eyelids_to_globe(
    *,
    upper: tuple[Point2, ...],
    lower: tuple[Point2, ...],
    inner_canthus: Point2,
    outer_canthus: Point2,
    center: Vec3,
    caruncle: tuple[Point2, ...] = (),
    epicanthus: tuple[Point2, ...] = (),
    radius: float,
    basis: OcularBasis3D,
    self_intersections_2d: int = 0,
) -> EyelidSurfaceCoupling:
    """Resolve lid depth and near/far canthi while retaining the 2D aperture owner."""
    if radius <= 0 or not math.isfinite(radius):
        raise ValueError("globe radius must be finite and > 0")
    upper3 = _lift_trace(upper, center, radius, basis)
    lower3 = _lift_trace(lower, center, radius, basis)
    inner3, _ = _surface_point(inner_canthus, center, radius, basis, orbital_x=radius * 1.05, orbital_y=radius * .72, orbital_z=radius * 1.03)
    outer3, _ = _surface_point(outer_canthus, center, radius, basis, orbital_x=radius * 1.05, orbital_y=radius * .72, orbital_z=radius * 1.03)
    camera_forward = (0.0, 0.0, 1.0)
    inner_depth = _depth(inner3, center, camera_forward)
    outer_depth = _depth(outer3, center, camera_forward)
    if math.isclose(inner_depth, outer_depth, abs_tol=1e-10):
        near, far = "inner", "outer"
    elif inner_depth > outer_depth:
        near, far = "inner", "outer"
    else:
        near, far = "outer", "inner"
    caruncle3 = _lift_trace(caruncle, center, radius, basis) if caruncle else None
    epicanthus3 = _lift_trace(epicanthus, center, radius, basis) if epicanthus else None
    return EyelidSurfaceCoupling(
        upper=upper3, lower=lower3, caruncle=caruncle3, epicanthus=epicanthus3,
        inner_canthus=inner3, outer_canthus=outer3,
        near_canthus=near, far_canthus=far,
        near_canthus_depth=max(inner_depth, outer_depth),
        far_canthus_depth=min(inner_depth, outer_depth),
        self_intersections_2d=self_intersections_2d,
    )
