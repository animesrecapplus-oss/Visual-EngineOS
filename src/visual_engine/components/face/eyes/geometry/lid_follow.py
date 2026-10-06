from __future__ import annotations

import math

def _apply_gaze_lid_follow(
    upper: tuple[tuple[float, float], ...],
    lower: tuple[tuple[float, float], ...],
    normalized_x: float,
    normalized_y: float,
    visible_half_height: float,
    strength: float,
    rotation_deg: float = 0.0,
) -> tuple[tuple[tuple[float, float], ...], tuple[tuple[float, float], ...]]:
    """Deform the aperture subtly in response to gaze direction.

    This is deliberately a bounded gaze-follow behaviour, not the future
    anatomical eyelid solver. The lids follow the ocular movement while their
    canthi remain shared, so looking down/up changes the visible aperture rather
    than leaving a rigid almond around a moving internal assembly.
    """
    follow = min(1.0, max(0.0, strength))
    vertical = normalized_y * visible_half_height * 0.10 * follow
    horizontal = 0.0
    angle = math.radians(rotation_deg)
    ux, uy = math.cos(angle), math.sin(angle)
    vx, vy = -math.sin(angle), math.cos(angle)

    def deform(points: tuple[tuple[float, float], ...], direction: float) -> tuple[tuple[float, float], ...]:
        n = max(len(points) - 1, 1)
        out = []
        for i, (x, y) in enumerate(points):
            t = i / n
            # C1-safe window: value and first derivative vanish at both canthi.
            # A fractional power here leaked a horizontal endpoint tangent into
            # the canthus bridge under gaze-follow, especially at tiny openings.
            interior = math.sin(math.pi * t) ** 2
            # Both lids translate with gaze; the upper lid follows more strongly,
            # reducing the aperture naturally when the eye looks up or down.
            local_x = horizontal * interior * (1.0 if direction < 0 else 0.35)
            local_y = direction * vertical * interior
            x2 = x + local_x * ux + local_y * vx
            y2 = y + local_x * uy + local_y * vy
            out.append((x2, y2))
        return tuple(out)

    upper2 = deform(upper, 1.0)
    lower2 = deform(lower, 0.35)
    # The endpoint window is exactly zero, so the original rotated canthus
    # coordinates are already preserved. Never re-anchor only X: that would break
    # the local vertical separation after intrinsic eye rotation.
    return upper2, lower2
