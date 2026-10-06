from __future__ import annotations
from dataclasses import dataclass
import math
from visual_engine.math import Vec2

@dataclass(frozen=True, slots=True)
class Circle:
    center: Vec2
    radius: float
    def __post_init__(self) -> None:
        if not math.isfinite(self.radius) or self.radius <= 0:
            raise ValueError("Circle radius must be finite and > 0")
    def bounds(self) -> tuple[float, float, float, float]:
        r = self.radius
        return self.center.x-r, self.center.y-r, self.center.x+r, self.center.y+r
    def contains(self, point: Vec2) -> bool:
        dx = point.x-self.center.x; dy = point.y-self.center.y
        return dx*dx + dy*dy <= self.radius*self.radius
