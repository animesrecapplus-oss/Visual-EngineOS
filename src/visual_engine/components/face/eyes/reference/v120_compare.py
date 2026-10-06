from __future__ import annotations

"""V1.20 fixed-frame source-pixel comparison and calibration aggregation."""

import math
from typing import Any, Iterable

from .digitization import ReferenceSample
from .overlay import ReferenceEngineAlignment, overlay_metrics

def _normal_span(points: Iterable[tuple[float, float]], axis: tuple[float, float], origin: tuple[float, float]) -> float:
    nx, ny = -axis[1], axis[0]
    values = []
    ox, oy = origin
    for x, y in points:
        values.append((x - ox) * nx + (y - oy) * ny)
    return max(values) - min(values) if values else 0.0


def build_fixed_reference_engine_alignment(sample: ReferenceSample, engine: Any) -> ReferenceEngineAlignment:
    """Build the non-fitting affine comparison frame.

    The terminal axis is the only longitudinal reference. Normal scale is measured
    from the digitized upper/lower source curves and the corresponding engine lid
    curves. No control point, curvature or follow strength is optimized here.
    """
    if not sample.upper or not sample.lower or not sample.medial_terminal_px or not sample.lateral_terminal_px:
        raise ValueError("complete upper/lower curves and both terminals are required")
    rx0, ry0 = sample.medial_terminal_px
    rx1, ry1 = sample.lateral_terminal_px
    rdx, rdy = rx1 - rx0, ry1 - ry0
    rlen = math.hypot(rdx, rdy)
    if rlen <= 1e-12:
        raise ValueError("reference terminal axis is degenerate")
    raxis = (rdx / rlen, rdy / rlen)
    ref_span = _normal_span(sample.upper.points_px + sample.lower.points_px, raxis, sample.medial_terminal_px)
    if ref_span <= 1e-12:
        raise ValueError("reference normal span is degenerate")
    ex0, ey0 = engine.inner_canthus
    ex1, ey1 = engine.outer_canthus
    edx, edy = ex1 - ex0, ey1 - ey0
    elen = math.hypot(edx, edy)
    if elen <= 1e-12:
        raise ValueError("engine terminal axis is degenerate")
    eaxis = (edx / elen, edy / elen)
    engine_span = _normal_span(engine.upper_lid_points + engine.lower_lid_points, eaxis, engine.inner_canthus)
    if engine_span <= 1e-12:
        raise ValueError("engine normal span is degenerate")
    return ReferenceEngineAlignment(
        reference_medial_px=sample.medial_terminal_px,
        reference_lateral_px=sample.lateral_terminal_px,
        engine_medial=engine.inner_canthus,
        engine_lateral=engine.outer_canthus,
        reference_normal_scale=ref_span,
        engine_normal_scale=engine_span,
    )


def _flatten_overlay_metrics(metrics: dict[str, Any]) -> dict[str, float]:
    """Extract scalar errors used by the calibration aggregate."""
    result: dict[str, float] = {}
    for prefix in ("upper_error", "lower_error"):
        block = metrics.get(prefix)
        if isinstance(block, dict):
            for key in ("mean_error", "max_error", "rms_error"):
                if key in block:
                    result[f"{prefix}.{key}"] = float(block[key])
    for key, value in metrics.items():
        if key.endswith("_error") and isinstance(value, (int, float)):
            result[key] = float(value)
        elif key.endswith("_error_deg") and isinstance(value, (int, float)):
            result[key] = float(value)
    return result


def evaluate_follow_strength_sample(sample: ReferenceSample, *, strengths: Iterable[float], build_engine) -> dict[str, Any]:
    """Evaluate actual engine geometry against one approved pixel sample.

    ``build_engine`` is injected so the reference layer remains independent from
    the generator. It must accept ``follow_strength`` and return ``EyeGeometry``.
    Every tested strength is rendered/measured independently; no interpolation is
    performed between values.
    """
    if not sample.complete_curve_digitization:
        raise ValueError(f"sample {sample.sample_id} is incomplete for pixel comparison")
    values = tuple(float(v) for v in strengths)
    if len(values) < 2 or len(set(values)) != len(values):
        raise ValueError("at least two distinct follow-strength values are required")
    results: dict[str, Any] = {"sample_id": sample.sample_id, "evaluations": {}}
    for strength in values:
        if not math.isfinite(strength) or not 0.0 <= strength <= 1.0:
            raise ValueError("follow strength must be finite and within [0,1]")
        engine = build_engine(strength)
        alignment = build_fixed_reference_engine_alignment(sample, engine)
        metrics = overlay_metrics(sample, engine, alignment)
        results["evaluations"][f"{strength:.6f}"] = {
            "follow_strength": strength,
            "metrics": metrics,
            "scalar_errors": _flatten_overlay_metrics(metrics),
        }
    return results


def aggregate_follow_strength_results(sample_results: Iterable[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate only common, actually evaluated strengths across independent samples."""
    rows = tuple(sample_results)
    if len(rows) < 2:
        raise ValueError("real-pixel calibration requires at least two approved independent samples")
    maps = [row.get("evaluations", {}) for row in rows]
    common = set(maps[0])
    for mapping in maps[1:]:
        common &= set(mapping)
    if len(common) < 2:
        raise ValueError("approved samples must share at least two tested strengths")
    aggregate: dict[str, Any] = {"sample_count": len(rows), "strengths": {}}
    for key in sorted(common, key=float):
        scalar_maps = [maps[i][key]["scalar_errors"] for i in range(len(rows))]
        metric_names = set(scalar_maps[0])
        for scalar in scalar_maps[1:]:
            metric_names &= set(scalar)
        if not metric_names:
            raise ValueError(f"no common scalar metrics for follow strength {key}")
        metrics = {}
        for name in sorted(metric_names):
            values = [float(s[name]) for s in scalar_maps]
            metrics[name] = {
                "mean": sum(values) / len(values),
                "rms": math.sqrt(sum(v * v for v in values) / len(values)),
                "max": max(values),
                "sample_count": len(values),
            }
        aggregate["strengths"][key] = metrics
    return aggregate


def select_candidate_strength(aggregate: dict[str, Any], *, metric: str = "upper_error.rms_error") -> dict[str, Any]:
    """Select the lowest *observed* metric as a candidate, never a promotion."""
    strengths = aggregate.get("strengths", {})
    if len(strengths) < 2:
        raise ValueError("candidate selection requires at least two evaluated strengths")
    available = []
    for key, metrics in strengths.items():
        if metric not in metrics:
            raise ValueError(f"metric {metric!r} missing for strength {key}")
        available.append((float(key), float(metrics[metric]["mean"])))
    value, error = min(available, key=lambda pair: (pair[1], pair[0]))
    return {
        "value": value,
        "metric": metric,
        "mean_error": error,
        "sample_count": int(aggregate["sample_count"]),
        "status": "candidate_only",
        "nonclaim": "Lowest measured error is not visual acceptance and is not promoted engine truth.",
    }
