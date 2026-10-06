from __future__ import annotations

from dataclasses import dataclass

Point2 = tuple[float, float]


@dataclass(frozen=True, slots=True)
class ApertureOcclusion:
    """Measured 2D clipping of projected ocular children by the lid aperture."""

    iris_fraction: float
    pupil_fractions: tuple[float, ...]
    iris_state: str
    pupil_states: tuple[str, ...]


def _inside(point: Point2, polygon: tuple[Point2, ...]) -> bool:
    if len(polygon) < 3:
        return False
    x, y = point
    inside = False
    j = len(polygon) - 1
    for i, (xi, yi) in enumerate(polygon):
        xj, yj = polygon[j]
        crosses = (yi > y) != (yj > y)
        if crosses:
            x_at_y = (xj - xi) * (y - yi) / (yj - yi) + xi
            if x < x_at_y:
                inside = not inside
        j = i
    return inside


def _fraction(points: tuple[Point2, ...], polygon: tuple[Point2, ...]) -> float:
    if not points:
        return 0.0
    return sum(_inside(p, polygon) for p in points) / len(points)


def _state(fraction: float) -> str:
    if fraction <= 0.0:
        return "hidden"
    if fraction >= 1.0:
        return "visible"
    return "partially_visible"


def measure_aperture_occlusion(
    *,
    aperture: tuple[Point2, ...],
    iris: tuple[Point2, ...],
    pupils: tuple[tuple[Point2, ...], ...],
) -> ApertureOcclusion:
    """Measure clipping using actual projected samples; renderer still owns clipping."""
    iris_fraction = _fraction(iris, aperture)
    pupil_fractions = tuple(_fraction(pupil, aperture) for pupil in pupils)
    return ApertureOcclusion(
        iris_fraction=iris_fraction,
        pupil_fractions=pupil_fractions,
        iris_state=_state(iris_fraction),
        pupil_states=tuple(_state(value) for value in pupil_fractions),
    )
