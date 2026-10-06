from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence

from visual_engine.math import Vec2
from .composition import Frame


@dataclass(frozen=True, slots=True)
class RectRegion:
    """Axis-aligned forbidden region in frame coordinates."""
    x: float
    y: float
    width: float
    height: float

    def __post_init__(self) -> None:
        if self.width < 0 or self.height < 0:
            raise ValueError("region dimensions must be >= 0")

    def contains(self, point: Vec2, margin: float = 0.0) -> bool:
        return (self.x-margin <= point.x <= self.x+self.width+margin and
                self.y-margin <= point.y <= self.y+self.height+margin)


@dataclass(frozen=True, slots=True)
class EyePlacementRequest:
    count: int
    eye_width: float
    eye_height: float
    min_gap: float = 0.15
    margin: float = 0.05

    def __post_init__(self) -> None:
        if self.count < 1 or self.eye_width <= 0 or self.eye_height <= 0 or self.min_gap < 0:
            raise ValueError("invalid eye placement request")
        if not 0 <= self.margin < 0.5:
            raise ValueError("margin must be in [0, 0.5)")


def _inside(point: Vec2, frame: Frame, half_w: float, half_h: float, margin: float) -> bool:
    return (margin*frame.width + half_w <= point.x <= frame.width-margin*frame.width-half_w and
            margin*frame.height + half_h <= point.y <= frame.height-margin*frame.height-half_h)


def _separation_ok(point: Vec2, chosen: Sequence[Vec2], half_w: float, half_h: float, gap: float) -> bool:
    min_dx = 2*half_w + gap
    min_dy = 2*half_h + gap
    for other in chosen:
        # Elliptic normalized separation: conservative enough to prevent visual overlap.
        dx = abs(point.x-other.x)/max(min_dx, 1e-9)
        dy = abs(point.y-other.y)/max(min_dy, 1e-9)
        if dx*dx + dy*dy < 1.0:
            return False
    return True


def solve_eye_positions(
    frame: Frame,
    request: EyePlacementRequest,
    *,
    forbidden: Sequence[RectRegion] = (),
    candidate_resolution: int = 18,
) -> tuple[Vec2, ...]:
    """Deterministically distribute N eye footprints across a frame.

    This is deliberately host-agnostic: a face, forehead, hand, arm, creature body,
    etc. supplies forbidden regions. It does not assume that eyes belong to a face.
    """
    if candidate_resolution < 4:
        raise ValueError("candidate_resolution must be >= 4")
    half_w, half_h = request.eye_width/2, request.eye_height/2
    candidates: list[Vec2] = []
    for iy in range(candidate_resolution):
        y = frame.height*(iy+0.5)/candidate_resolution
        for ix in range(candidate_resolution):
            x = frame.width*(ix+0.5)/candidate_resolution
            p = Vec2(x, y)
            if not _inside(p, frame, half_w, half_h, request.margin):
                continue
            if any(r.contains(p, margin=max(half_w, half_h)) for r in forbidden):
                continue
            candidates.append(p)
    if not candidates:
        raise ValueError("no valid eye placement candidates")

    chosen: list[Vec2] = []
    # First eye: closest to frame centre. Subsequent eyes: farthest-point sampling.
    centre = Vec2(frame.width/2, frame.height/2)
    while len(chosen) < request.count:
        valid = [p for p in candidates if p not in chosen and _separation_ok(p, chosen, half_w, half_h, request.min_gap)]
        if not valid:
            raise ValueError("cannot place requested number of eyes with current spacing/forbidden constraints")
        if not chosen:
            best = min(valid, key=lambda p: (p.x-centre.x)**2 + (p.y-centre.y)**2)
        else:
            def score(p: Vec2) -> tuple[float, float, float]:
                nearest = min(math.hypot(p.x-q.x, p.y-q.y) for q in chosen)
                # Prefer positions that improve frame coverage; deterministic tie-breakers.
                edge = min(p.x, frame.width-p.x, p.y, frame.height-p.y)
                return (nearest, edge, -(p.y + p.x*1e-6))
            best = max(valid, key=score)
        chosen.append(best)
    return tuple(chosen)
