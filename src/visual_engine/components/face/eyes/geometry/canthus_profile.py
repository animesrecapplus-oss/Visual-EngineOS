from __future__ import annotations

"""Application of V1.6 per-endpoint tangent profiles to sampled lid margins."""

import math

from ..morphology.canthus_profile import CanthusEndpointTangentProfile

Point = tuple[float, float]


def _unit(dx: float, dy: float) -> Point:
    norm = math.hypot(dx, dy)
    if norm <= 1e-15:
        return 1.0, 0.0
    return dx / norm, dy / norm


def _rotate_direction(direction: Point, angle_deg: float) -> Point:
    angle = math.radians(angle_deg)
    c, s = math.cos(angle), math.sin(angle)
    return direction[0] * c - direction[1] * s, direction[0] * s + direction[1] * c


def apply_endpoint_profile(
    points: list[Point],
    *,
    at_end: bool,
    baseline_handle: float,
    profile: CanthusEndpointTangentProfile,
) -> None:
    """Rewrite only the first/last two interior samples for one endpoint.

    The endpoint itself never moves.  The second interior sample remains exactly
    twice the first handle away from the endpoint, preserving the renderer's
    endpoint derivative convention.  Influence is applied after V1.5 has chosen
    a safe baseline handle, so V1.6 cannot silently discard V1.5's bounds.
    """
    if len(points) < 3:
        raise ValueError("at least three lid samples are required")
    if not math.isfinite(baseline_handle) or baseline_handle <= 0.0:
        raise ValueError("baseline canthus tangent handle must be finite and > 0")

    if at_end:
        endpoint = points[-1]
        dx, dy = points[-3][0] - endpoint[0], points[-3][1] - endpoint[1]
        indices = (-2, -3)
    else:
        endpoint = points[0]
        dx, dy = points[2][0] - endpoint[0], points[2][1] - endpoint[1]
        indices = (1, 2)

    ux, uy = _unit(dx, dy)
    influence = profile.influence
    rotated = _rotate_direction((ux, uy), profile.angle_deg * influence)
    scale = (1.0 - influence) + influence * profile.length_scale
    handle = baseline_handle * scale

    # Keep the opt-in profile local. A strict one-spacing cap prevents the new
    # control from becoming an accidental global contour deformation; the actual
    # self-intersection checks remain the final fail-closed guard.
    local_spacing = math.hypot(dx, dy)
    handle = min(handle, max(local_spacing * 0.95, 1e-15))
    if handle <= 1e-15:
        raise ValueError("canthus endpoint profile collapsed its tangent handle")

    p1 = (endpoint[0] + rotated[0] * handle, endpoint[1] + rotated[1] * handle)
    p2 = (endpoint[0] + rotated[0] * 2.0 * handle, endpoint[1] + rotated[1] * 2.0 * handle)
    points[indices[0]], points[indices[1]] = p1, p2
