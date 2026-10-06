from __future__ import annotations

import math

Point = tuple[float, float]

def build_epicanthic_fold(top: Point, bottom: Point, strength: float, scale: float, *, interior_target: Point | None = None) -> tuple[Point, ...]:
    """Build the optional medial skin fold without closing the aperture.

    The fold is an external/medial soft-tissue cue, not the canthus terminal and
    not the caruncle. Its lateral direction is derived from the eye centre so a
    mirrored pair does not receive a fold on the wrong side.
    """
    if strength <= 0:
        return ()
    if interior_target is None:
        interior_target = ((top[0] + bottom[0]) * .5 + scale, (top[1] + bottom[1]) * .5)
    vx, vy = interior_target[0] - top[0], interior_target[1] - top[1]
    norm = math.hypot(vx, vy)
    if norm <= 1e-15:
        return ()
    ux, uy = vx / norm, vy / norm
    # The fold must sit underneath the canthal borders rather than sharing their
    # exact endpoints. This small inward inset is geometry, not a renderer trick;
    # it prevents the epicanthus from being painted directly on the black corner.
    inset = min(max(scale * 0.08, 1e-9), norm * 0.25)
    top_i = (top[0] + ux * inset, top[1] + uy * inset)
    bottom_i = (bottom[0] + ux * inset, bottom[1] + uy * inset)
    depth = strength * max(scale, 1e-15) * 0.22
    return tuple((
        top_i[0] + (bottom_i[0]-top_i[0]) * u + ux * depth * math.sin(math.pi*u),
        top_i[1] + (bottom_i[1]-top_i[1]) * u + uy * depth * math.sin(math.pi*u),
    ) for u in (0.0, 0.125, 0.25, 0.375, 0.5, 0.625, 0.75, 0.875, 1.0))
