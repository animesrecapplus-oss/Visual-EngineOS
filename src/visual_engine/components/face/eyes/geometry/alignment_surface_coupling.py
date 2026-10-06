from __future__ import annotations

import math

from .projection3d import Camera3D, project_point
from .spherical_assembly import Vec3
from .view_axis import OcularBasis3D

Point2 = tuple[float, float]


def _dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _add(a: Vec3, b: Vec3) -> Vec3:
    return a[0] + b[0], a[1] + b[1], a[2] + b[2]


def _scale(a: Vec3, s: float) -> Vec3:
    return a[0] * s, a[1] * s, a[2] * s


def _norm(v: Vec3) -> float:
    return math.sqrt(_dot(v, v))


def _unit(v: Vec3) -> Vec3:
    n = _norm(v)
    if n <= 1e-12 or not math.isfinite(n):
        raise ValueError("alignment surface vector must be finite and non-zero")
    return tuple(x / n for x in v)


def _surface_world(point: Point2, center: Vec3, radius: float, basis: OcularBasis3D) -> Vec3:
    """Attach a lid sample to the front globe in the *ocular* frame.

    The semantic lid sample remains face-owned, but its soft-tissue surface may
    slide over the rotating globe. Endpoints are handled separately by
    ``couple_lid_curve`` so canthi remain face anchors. This is the missing link
    between a fixed 2D aperture and the visibly changing eye opening in the
    alignment reference family.
    """
    lx = point[0] - center[0]
    ly = -(point[1] - center[1])
    radial2 = lx * lx + ly * ly
    limit = radius * 0.995
    if radial2 >= limit * limit:
        scale = limit / math.sqrt(radial2)
        lx *= scale
        ly *= scale
        radial2 = lx * lx + ly * ly
    lz = math.sqrt(max(radius * radius - radial2, 0.0))
    return _add(center, _add(_scale(basis.alignment_axis, lx), _add(_scale(basis.vertical_axis, ly), _scale(basis.view_axis, lz))))


def couple_lid_curve(
    points: tuple[Point2, ...],
    *,
    center: Vec3,
    radius: float,
    basis: OcularBasis3D,
    camera: Camera3D = Camera3D(),
    endpoint_weight_power: float = 1.75,
    follow_strength: float = 0.10,
) -> tuple[tuple[Point2, ...], tuple[Vec3, ...]]:
    """Project a lid surface over the globe while preserving both face canthi.

    ``points[0]`` and ``points[-1]`` are immutable face anchors. Interior samples
    progressively inherit the globe orientation. This is not a rigid rotation of
    the aperture: it is a surface-following deformation, which is what allows the
    visible eyelid shape to change while the canthi remain attached to the face.
    """
    if len(points) < 2:
        return points, ()
    if radius <= 0 or not math.isfinite(radius):
        raise ValueError("radius must be finite and > 0")
    if endpoint_weight_power <= 0 or not math.isfinite(endpoint_weight_power):
        raise ValueError("endpoint_weight_power must be finite and > 0")
    if not 0.0 <= follow_strength <= 1.0 or not math.isfinite(follow_strength):
        raise ValueError("follow_strength must be within [0,1]")
    if abs(basis.view_axis[2]) < 1e-10 and not camera.orthographic:
        raise ValueError("perspective projection is degenerate for the requested view axis")

    projected: list[Point2] = []
    world: list[Vec3] = []
    n = len(points) - 1
    for i, point in enumerate(points):
        t = i / n
        if i == 0 or i == n:
            # Canthi are face-owned anchors. They must not drift when the globe
            # changes orientation.
            p3 = (point[0], -point[1], 0.0)
            p2 = point
        else:
            surface = _surface_world(point, center, radius, basis)
            p3 = surface
            # Smoothly reduce ocular coupling toward each canthus. This avoids a
            # hard kink where a moving globe meets an immovable facial corner.
            edge = min(t, 1.0 - t) * 2.0
            weight = follow_strength * (min(1.0, max(0.0, edge)) ** endpoint_weight_power)
            face_anchor = (point[0], -point[1], 0.0)
            # Interpolate in 3D, then project. This is critical: interpolating a
            # 2D projection and reusing an unrelated Z creates a mathematically
            # inconsistent depth surface and can manufacture false occlusion.
            p3 = tuple(face_anchor[j] + (surface[j] - face_anchor[j]) * weight for j in range(3))
            p2 = project_point(p3, camera)
        projected.append(p2)
        world.append(p3)
    return tuple(projected), tuple(world)


def rebuild_coupled_aperture(
    upper: tuple[Point2, ...],
    lower: tuple[Point2, ...],
    *,
    outer_bridge_mode: str,
    inner_bridge_mode: str,
) -> tuple[tuple[Point2, ...], tuple[Point2, ...], tuple[Point2, ...], tuple[Point2, ...], tuple[Point2, ...]]:
    """Rebuild renderer-neutral aperture topology after surface coupling.

    Kept outside the main builder so the audited eye builder remains below the
    repository's 250-line maintainability budget.
    """
    from .continuity import assess_contour_continuity, build_canthus_bridges, closed_contour_samples
    from .invariants import assert_finite_contour, has_self_intersection
    contour = tuple(upper + tuple(reversed(lower)))
    assert_finite_contour(contour)
    if has_self_intersection(contour):
        raise ValueError("alignment-coupled eyelid contour self-intersection detected")
    outer_bridge = build_canthus_bridges(upper, lower)[0] if outer_bridge_mode == "bridge" else ()
    inner_bridge = build_canthus_bridges(upper, lower)[1] if inner_bridge_mode == "bridge" else ()
    continuity = assess_contour_continuity(upper, lower, outer_bridge, inner_bridge)
    if not continuity.valid:
        raise ValueError(f"alignment-coupled continuity invariant failed: max_error={continuity.max_error:.3e}")
    closed = closed_contour_samples(upper, lower, outer_bridge, inner_bridge)
    assert_finite_contour(closed)
    if has_self_intersection(closed):
        raise ValueError("alignment-coupled canthus self-intersection detected")
    return upper, lower, contour, outer_bridge, inner_bridge
