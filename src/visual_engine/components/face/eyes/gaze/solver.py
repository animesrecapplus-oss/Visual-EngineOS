from dataclasses import dataclass
import math
from numbers import Real

from ..contracts.types import GazeDirection
from ..contracts.validation import _finite

def _finite_real(value: object) -> bool:
    """Fast-path common Python numerics while retaining strict Real semantics."""
    value_type = type(value)
    if value_type is bool:
        return False
    if value_type is float or value_type is int:
        try:
            return math.isfinite(value)
        except (OverflowError, TypeError):
            return False
    if not isinstance(value, Real):
        return False
    try:
        return math.isfinite(value)
    except (OverflowError, TypeError):
        return False

@dataclass(frozen=True, slots=True)
class GazeSolution:
    """Resolved eye-local gaze vector and pupil-center offset.

    The vector is normalized to the requested direction and then limited by the
    actual sampled eye aperture. It is deliberately independent of rendering.
    """

    direction_x: float
    direction_y: float
    normalized_x: float
    normalized_y: float
    offset_x: float
    offset_y: float
    limit: float
    requested_magnitude: float
    clamped: bool


@dataclass(frozen=True, slots=True)
class Gaze:
    x: float = 0.0
    y: float = 0.0
    strength: float = 1.0
    direction: GazeDirection = "center"
    target: tuple[float, float] | None = None
    amplitude: float = 1.0

    def __post_init__(self) -> None:
        # Local input invariant: authored gaze numerics are real, non-bool and finite
        # before any solver/transform arithmetic; no numeric coercion is performed.
        numeric = (self.x, self.y, self.strength, self.amplitude)
        for value in numeric:
            if not _finite_real(value):
                raise ValueError("gaze values must be finite numeric values")
        if self.strength < 0 or self.amplitude < 0:
            raise ValueError("invalid gaze")
        if self.target is not None:
            if not isinstance(self.target, tuple) or len(self.target) != 2:
                raise ValueError("gaze target must be a finite (x, y) pair")
            for value in self.target:
                if not _finite_real(value):
                    raise ValueError("gaze target must be a finite (x, y) pair")
        if self.direction not in {"center", "up", "down", "left", "right", "upper_left", "upper_right", "lower_left", "lower_right"}:
            raise ValueError("unknown gaze direction")

    def vector(self, *, center: tuple[float, float] = (0.0, 0.0)) -> tuple[float, float]:
        if self.target is not None:
            return (self.target[0] - center[0] + self.x, self.target[1] - center[1] + self.y)
        named = {
            "center": (0.0, 0.0), "up": (0.0, -1.0), "down": (0.0, 1.0),
            "left": (-1.0, 0.0), "right": (1.0, 0.0),
            "upper_left": (-0.70710678, -0.70710678), "upper_right": (0.70710678, -0.70710678),
            "lower_left": (-0.70710678, 0.70710678), "lower_right": (0.70710678, 0.70710678),
        }[self.direction]
        return named[0] + self.x, named[1] + self.y


@dataclass(frozen=True, slots=True)
class BinocularGazeSolution:
    """Pair-level gaze diagnostics for two eyes sharing one target.

    This is intentionally 2D: the two eye centers and the target live in the
    same scene plane. It does not pretend to be a 3D ocular/optic model.
    """

    left_vector: tuple[float, float]
    right_vector: tuple[float, float]
    left_angle_deg: float
    right_angle_deg: float
    convergence_angle_deg: float
    target: tuple[float, float]


class BinocularGazeSolver:
    """Resolve a common target for a pair of eyes in scene coordinates."""

    @staticmethod
    def solve(
        left_center: tuple[float, float],
        right_center: tuple[float, float],
        target: tuple[float, float],
    ) -> BinocularGazeSolution:
        lx, ly = target[0] - left_center[0], target[1] - left_center[1]
        rx, ry = target[0] - right_center[0], target[1] - right_center[1]
        if not _finite((left_center[0], left_center[1], right_center[0], right_center[1], target[0], target[1])):
            raise ValueError("binocular gaze coordinates must be finite")
        if math.hypot(lx, ly) <= 1e-12 or math.hypot(rx, ry) <= 1e-12:
            raise ValueError("binocular gaze target cannot coincide with an eye center")

        left_angle = math.degrees(math.atan2(ly, lx))
        right_angle = math.degrees(math.atan2(ry, rx))
        # Smallest angular separation in [0, 180].
        delta = abs((left_angle - right_angle + 180.0) % 360.0 - 180.0)
        return BinocularGazeSolution(
            left_vector=(lx, ly),
            right_vector=(rx, ry),
            left_angle_deg=left_angle,
            right_angle_deg=right_angle,
            convergence_angle_deg=delta,
            target=target,
        )


class GazeSolver:
    """Resolve gaze against the actual eye aperture and pupil footprint.

    The solver works in the eye's local coordinate system. It does not assume a
    face, head, or renderer, so the same solver can later serve non-human eyes.
    """

    @staticmethod
    def _ray_polygon_limit(dx: float, dy: float, points: tuple[tuple[float, float], ...]) -> float:
        """Distance from the origin to the first contour intersection on a ray."""
        best = math.inf
        n = len(points)
        for i in range(n):
            ax, ay = points[i]
            bx, by = points[(i + 1) % n]
            ex, ey = bx - ax, by - ay
            cross = dx * ey - dy * ex
            if abs(cross) < 1e-12:
                continue
            t = (ax * ey - ay * ex) / cross
            u = (ax * dy - ay * dx) / cross
            if t >= 0.0 and 0.0 <= u <= 1.0:
                best = min(best, t)
        if not math.isfinite(best):
            return 0.0
        return best

    @staticmethod
    def solve(
        gaze: Gaze,
        contour: tuple[tuple[float, float], ...],
        *,
        center: tuple[float, float] = (0.0, 0.0),
        iris_center: tuple[float, float] = (0.0, 0.0),
        iris_rx: float,
        iris_ry: float,
        pupil_rx: float,
        pupil_ry: float,
    ) -> GazeSolution:
        vx, vy = gaze.vector(center=center)
        requested = math.hypot(vx, vy) * gaze.strength * gaze.amplitude
        if requested <= 1e-12:
            return GazeSolution(
                vx, vy, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, False
            )
        mag = math.hypot(vx, vy)
        nx, ny = vx / mag, vy / mag

        # The gaze center is allowed to reach the actual eyelid aperture. The
        # ocular assembly is rendered behind the sclera clip, so its iris/pupil
        # footprint may extend beyond the white-eye perimeter and be naturally
        # cropped at the canthi/upper/lower margins. Keeping a pupil footprint
        # margin here would prevent the intended extreme-corner gaze.
        limit = max(GazeSolver._ray_polygon_limit(nx, ny, contour), 0.0)
        distance = min(requested, limit)
        ox, oy = nx * distance, ny * distance
        return GazeSolution(
            vx, vy, nx, ny, ox, oy, limit, requested, distance + 1e-12 < requested
        )
