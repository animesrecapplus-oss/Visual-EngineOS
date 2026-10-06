from __future__ import annotations

import math
from typing import Any

from .digitization import Point, ReferenceCurve, ReferenceSample


def _distance(a: Point, b: Point) -> float:
    return math.hypot(b[0] - a[0], b[1] - a[1])


def _angle(v: Point) -> float:
    return math.degrees(math.atan2(v[1], v[0]))


def _tangent(points: tuple[Point, ...], i: int, radius: int = 1) -> Point:
    j0 = max(0, i - radius)
    j1 = min(len(points) - 1, i + radius)
    return _unit((points[j1][0] - points[j0][0], points[j1][1] - points[j0][1]))


def _unit(v: Point) -> Point:
    n = math.hypot(v[0], v[1])
    if n <= 1e-15:
        raise ValueError("degenerate tangent")
    return v[0] / n, v[1] / n


def _turn_angle(a: Point, b: Point) -> float:
    dot = max(-1.0, min(1.0, a[0] * b[0] + a[1] * b[1]))
    return math.degrees(math.acos(dot))


def curve_metrics(curve: ReferenceCurve) -> dict[str, Any]:
    """Return descriptive geometry metrics without fitting a hidden style model."""
    pts = curve.points_px
    segment_lengths = [_distance(a, b) for a, b in zip(pts, pts[1:])]
    cumulative = [0.0]
    for length in segment_lengths:
        cumulative.append(cumulative[-1] + length)
    curvatures = []
    for i in range(1, len(pts) - 1):
        t0 = _tangent(pts, i - 1)
        t1 = _tangent(pts, i + 1)
        ds = max((cumulative[i + 1] - cumulative[i - 1]) * 0.5, 1e-9)
        curvatures.append(_turn_angle(t0, t1) * math.pi / 180.0 / ds)
    return {
        "arc_length_px": cumulative[-1],
        "start_tangent_deg": _angle(curve.tangent_start),
        "end_tangent_deg": _angle(curve.tangent_end),
        "max_discrete_curvature_px_inv": max(curvatures) if curvatures else None,
        "mean_discrete_curvature_px_inv": (sum(curvatures) / len(curvatures)) if curvatures else None,
        "curvature_peak_index": (1 + max(range(len(curvatures)), key=curvatures.__getitem__)) if curvatures else None,
    }


def endpoint_metrics(curve: ReferenceCurve, *, endpoint: str, tangent_deviation_deg: float = 10.0) -> dict[str, Any]:
    """Measure each endpoint independently.

    ``tangent_deviation_deg`` is an explicit analysis threshold, not an inferred
    anatomical constant. Keeping it in the result prevents a hidden calibration
    convention from being mistaken for source truth.
    """
    if endpoint not in {"start", "end"}:
        raise ValueError("endpoint must be start or end")
    pts = curve.points_px if endpoint == "start" else tuple(reversed(curve.points_px))
    base = _tangent(pts, 0)
    cumulative = 0.0
    transition_length = 0.0
    for i in range(1, len(pts) - 1):
        cumulative += _distance(pts[i - 1], pts[i])
        current = _tangent(pts, i)
        if _turn_angle(base, current) >= tangent_deviation_deg:
            transition_length = cumulative
            break
    else:
        transition_length = cumulative
    return {
        "endpoint": endpoint,
        "endpoint_tangent_deg": _angle(base),
        "tangent_stability_threshold_deg": tangent_deviation_deg,
        "transition_length_px": transition_length,
    }


def measure_reference_sample_v19(sample: ReferenceSample, *, tangent_deviation_deg: float = 10.0) -> dict[str, Any]:
    """Produce the V1.9 calibration record from fields that actually exist."""
    result: dict[str, Any] = {
        "sample_id": sample.sample_id,
        "family": sample.family.value,
        "upper": curve_metrics(sample.upper) if sample.upper else None,
        "lower": curve_metrics(sample.lower) if sample.lower else None,
        "inner_upper": endpoint_metrics(sample.upper, endpoint="start", tangent_deviation_deg=tangent_deviation_deg) if sample.upper else None,
        "outer_upper": endpoint_metrics(sample.upper, endpoint="end", tangent_deviation_deg=tangent_deviation_deg) if sample.upper else None,
        "inner_lower": endpoint_metrics(sample.lower, endpoint="start", tangent_deviation_deg=tangent_deviation_deg) if sample.lower else None,
        "outer_lower": endpoint_metrics(sample.lower, endpoint="end", tangent_deviation_deg=tangent_deviation_deg) if sample.lower else None,
        "caruncle": None,
        "epicanthus": curve_metrics(sample.epicanthus) if sample.epicanthus else None,
    }
    if sample.caruncle_polygon_px:
        xs = [p[0] for p in sample.caruncle_polygon_px]
        ys = [p[1] for p in sample.caruncle_polygon_px]
        result["caruncle"] = {
            "width_px": max(xs) - min(xs),
            "height_px": max(ys) - min(ys),
            "point_count": len(sample.caruncle_polygon_px),
            "color_rgb": getattr(sample, "caruncle_color_rgb", None),
            "opacity": getattr(sample, "caruncle_opacity", None),
        }
    return result
