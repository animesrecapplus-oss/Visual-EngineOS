from __future__ import annotations
from dataclasses import dataclass
import math

@dataclass(frozen=True, slots=True)
class Vec2:
    x: float
    y: float
    def __post_init__(self) -> None:
        if not math.isfinite(self.x) or not math.isfinite(self.y):
            raise ValueError("Vec2 components must be finite")
    def __add__(self, other: "Vec2") -> "Vec2": return Vec2(self.x + other.x, self.y + other.y)
    def __sub__(self, other: "Vec2") -> "Vec2": return Vec2(self.x - other.x, self.y - other.y)
    def __mul__(self, scalar: float) -> "Vec2": return Vec2(self.x * scalar, self.y * scalar)
    __rmul__ = __mul__
    def dot(self, other: "Vec2") -> float: return self.x * other.x + self.y * other.y
    def length(self) -> float: return math.hypot(self.x, self.y)
    def normalized(self, eps: float = 1e-12) -> "Vec2":
        n = self.length()
        if n <= eps: raise ValueError("Cannot normalize a near-zero vector")
        return self * (1.0 / n)
