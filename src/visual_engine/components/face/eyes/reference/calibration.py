from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import median
from typing import Any, Iterable, Literal

from .digitization import Point, ReferenceSample
from .trace import curve_metrics, endpoint_metrics

EyeSide = Literal["image_left", "image_right", "single"]


@dataclass(frozen=True, slots=True)
class TerminalResolution:
    """Semantic terminal mapping; source pixels never decide anatomy by x alone."""
    medial_px: Point
    lateral_px: Point
    inner_px: Point
    outer_px: Point
    side: EyeSide

    def __post_init__(self) -> None:
        if self.side not in {"image_left", "image_right", "single"}:
            raise ValueError("unknown eye side")
        if self.inner_px != self.medial_px or self.outer_px != self.lateral_px:
            raise ValueError("inner/outer terminals must map to medial/lateral")
        if self.side == "image_left" and self.medial_px[0] <= self.lateral_px[0]:
            raise ValueError("image-left front-view eye requires medial terminal right of lateral terminal")
        if self.side == "image_right" and self.medial_px[0] >= self.lateral_px[0]:
            raise ValueError("image-right front-view eye requires medial terminal left of lateral terminal")


def resolve_terminals(*, inner_px: Point, outer_px: Point, side: EyeSide, allow_oblique: bool = False) -> TerminalResolution:
    """Resolve inner→medial and outer→lateral; x-order is only a sanity check."""
    if side not in {"image_left", "image_right", "single"}:
        raise ValueError("unknown eye side")
    if not allow_oblique:
        TerminalResolution(inner_px, outer_px, inner_px, outer_px, side)
    return TerminalResolution(inner_px, outer_px, inner_px, outer_px, side)


def _angle_between(a: Point, b: Point) -> float:
    dot = max(-1.0, min(1.0, a[0] * b[0] + a[1] * b[1]))
    return math.degrees(math.acos(dot))


def _outward_tangent(curve, endpoint: str) -> Point:
    t = curve.tangent_start if endpoint == "start" else curve.tangent_end
    return t if endpoint == "start" else (-t[0], -t[1])


def canthus_pixel_metrics(sample: ReferenceSample, *, tangent_deviation_deg: float = 10.0) -> dict[str, Any]:
    """Measure terminal transitions and curvature from approved source pixels."""
    if not sample.upper or not sample.lower or not sample.medial_terminal_px or not sample.lateral_terminal_px:
        raise ValueError("canthus calibration requires both curves and both terminals")
    upper, lower = sample.upper, sample.lower
    return {
        "upper": {"curve": curve_metrics(upper), "start": endpoint_metrics(upper, endpoint="start", tangent_deviation_deg=tangent_deviation_deg),
                   "end": endpoint_metrics(upper, endpoint="end", tangent_deviation_deg=tangent_deviation_deg)},
        "lower": {"curve": curve_metrics(lower), "start": endpoint_metrics(lower, endpoint="start", tangent_deviation_deg=tangent_deviation_deg),
                   "end": endpoint_metrics(lower, endpoint="end", tangent_deviation_deg=tangent_deviation_deg)},
        "terminal_distance_px": math.dist(sample.medial_terminal_px, sample.lateral_terminal_px),
        "alignment_axis_angle_deg": math.degrees(math.atan2(sample.lateral_terminal_px[1] - sample.medial_terminal_px[1], sample.lateral_terminal_px[0] - sample.medial_terminal_px[0])),
        "medial_convergence_angle_deg": _angle_between(_outward_tangent(upper, "start"), _outward_tangent(lower, "start")),
        "lateral_convergence_angle_deg": _angle_between(_outward_tangent(upper, "end"), _outward_tangent(lower, "end")),
        "tangent_deviation_threshold_deg": tangent_deviation_deg,
        "direction_contract": "upper/lower curves are oriented inner(medial) -> outer(lateral)",
    }


def caruncle_metrics(sample: ReferenceSample) -> dict[str, Any] | None:
    """Measure only an explicitly digitized caruncle; absence stays unknown."""
    if not sample.caruncle_polygon_px:
        return None
    points = sample.caruncle_polygon_px
    xs, ys = zip(*points)
    cx, cy = sum(xs) / len(points), sum(ys) / len(points)
    terminal = sample.medial_terminal_px
    return {"polygon": points, "centroid_px": (cx, cy), "width_px": max(xs) - min(xs), "height_px": max(ys) - min(ys),
            "terminal_distance_px": math.dist((cx, cy), terminal) if terminal else None,
            "color_rgb": sample.caruncle_color_rgb, "opacity": sample.caruncle_opacity}


def epicanthus_status(sample: ReferenceSample, *, reviewer_status: str) -> dict[str, Any]:
    """Require explicit present/absent/unknown review; detection failure is not absence."""
    if reviewer_status not in {"present", "absent", "unknown"}:
        raise ValueError("epicanthus status must be present, absent or unknown")
    return {"status": reviewer_status, "curve": curve_metrics(sample.epicanthus) if reviewer_status == "present" and sample.epicanthus else None}


def sample_calibration_record(sample: ReferenceSample, *, eye_side: EyeSide, epicanthus_review: str = "unknown") -> dict[str, Any]:
    """Assemble approved observable fields without substituting missing measurements."""
    terminals = resolve_terminals(inner_px=sample.medial_terminal_px, outer_px=sample.lateral_terminal_px, side=eye_side, allow_oblique=True) if sample.medial_terminal_px and sample.lateral_terminal_px else None
    return {"sample_id": sample.sample_id, "family": sample.family.value,
            "terminals": {"medial_px": terminals.medial_px, "lateral_px": terminals.lateral_px} if terminals else None,
            "curves": {"upper": curve_metrics(sample.upper) if sample.upper else None, "lower": curve_metrics(sample.lower) if sample.lower else None},
            "canthus": canthus_pixel_metrics(sample), "caruncle": caruncle_metrics(sample),
            "epicanthus": epicanthus_status(sample, reviewer_status=epicanthus_review)}


def _read_path(row: dict[str, Any], path: str) -> Any:
    value: Any = row
    for part in path.split("."):
        value = value.get(part) if isinstance(value, dict) else None
    return value


def mor_ranges(records: Iterable[dict[str, Any]], *, field_paths: tuple[str, ...] = ()) -> dict[str, dict[str, Any]]:
    """Aggregate observed values only; at least two independent samples are required.

    ``confidence`` is a coverage score, not a statistical confidence interval or
    anatomical validity claim. A single source sample can never create a range.
    """
    rows = tuple(records)
    if len(rows) < 2:
        raise ValueError("MOR ranges require at least two independently approved samples")
    output: dict[str, dict[str, Any]] = {}
    for path in field_paths:
        values = []
        for row in rows:
            value = _read_path(row, path)
            if isinstance(value, (int, float)) and math.isfinite(value):
                values.append(float(value))
        if len(values) < 2:
            continue
        output[path] = {"observed_min": min(values), "observed_median": median(values), "observed_max": max(values),
                        "confidence": min(1.0, len(values) / 8.0), "source_sample_count": len(values),
                        "confidence_definition": "coverage-only; not an anatomical or statistical confidence interval"}
    return output


@dataclass(frozen=True, slots=True)
class FollowStrengthFit:
    """Auditable candidate for the V1.18 eyelid-surface follow parameter.

    This object is deliberately a *candidate*, not a promoted engine default.
    Pixel evidence must come from independently approved V1.11 samples and a
    human visual acceptance gate before the value can enter authoring defaults.
    """

    value: float
    mean_error: float
    sample_count: int
    evaluated_values: tuple[float, ...]
    status: str = "candidate_only"

    def __post_init__(self) -> None:
        if not math.isfinite(self.value) or not 0.0 <= self.value <= 1.0:
            raise ValueError("follow-strength candidate must be finite and within [0,1]")
        if not math.isfinite(self.mean_error) or self.mean_error < 0:
            raise ValueError("follow-strength mean error must be finite and >= 0")
        if self.sample_count < 2:
            raise ValueError("follow-strength calibration requires at least two independent samples")
        if self.status not in {"candidate_only", "visually_accepted"}:
            raise ValueError("unknown follow-strength calibration status")


def _validate_follow_strength_observations(observations: Iterable[dict[str, Any]]) -> tuple[dict[str, Any], ...]:
    """Validate only explicit approved observations; pending boxes are rejected."""
    rows = tuple(observations)
    if not rows:
        raise ValueError("no calibration observations supplied")
    seen: set[str] = set()
    validated: list[dict[str, Any]] = []
    for row in rows:
        sample_id = row.get("sample_id")
        if not isinstance(sample_id, str) or not sample_id:
            raise ValueError("calibration observation requires sample_id")
        if sample_id in seen:
            raise ValueError("calibration observations must use independent sample IDs")
        seen.add(sample_id)
        if row.get("reviewer_status") != "approved":
            raise ValueError(f"sample {sample_id} is not explicitly approved")
        errors = row.get("errors_by_strength")
        if not isinstance(errors, dict) or not errors:
            raise ValueError(f"sample {sample_id} has no errors_by_strength data")
        clean: dict[float, float] = {}
        for raw_strength, raw_error in errors.items():
            strength = float(raw_strength)
            error = float(raw_error)
            if not math.isfinite(strength) or not 0.0 <= strength <= 1.0:
                raise ValueError(f"sample {sample_id} contains invalid follow strength")
            if not math.isfinite(error) or error < 0:
                raise ValueError(f"sample {sample_id} contains invalid error")
            clean[strength] = error
        if len(clean) < 2:
            raise ValueError(f"sample {sample_id} requires at least two tested strengths")
        validated.append({"sample_id": sample_id, "errors_by_strength": clean})
    if len(validated) < 2:
        raise ValueError("follow-strength calibration requires at least two independently approved samples")
    common = set(validated[0]["errors_by_strength"])
    for row in validated[1:]:
        common &= set(row["errors_by_strength"])
    if len(common) < 2:
        raise ValueError("approved samples must share at least two tested follow-strength values")
    return tuple(validated)


def fit_eyelid_surface_follow_strength(observations: Iterable[dict[str, Any]]) -> FollowStrengthFit:
    """Find the lowest mean source-to-engine error over explicitly tested values.

    No interpolation, extrapolation, style assumption, or single-sample promotion
    is performed. The function only compares values actually evaluated by the caller.
    """
    rows = _validate_follow_strength_observations(observations)
    common = sorted(set(rows[0]["errors_by_strength"]).intersection(*(set(r["errors_by_strength"]) for r in rows[1:])))
    means = {strength: sum(r["errors_by_strength"][strength] for r in rows) / len(rows) for strength in common}
    best = min(means, key=lambda value: (means[value], value))
    return FollowStrengthFit(value=best, mean_error=means[best], sample_count=len(rows), evaluated_values=tuple(common))


def promote_eyelid_surface_follow_strength(candidate: FollowStrengthFit, *, human_visual_acceptance: bool) -> FollowStrengthFit:
    """Promote a fitted candidate only after an explicit human visual gate."""
    if not human_visual_acceptance:
        raise ValueError("follow-strength promotion requires explicit human visual acceptance")
    return FollowStrengthFit(value=candidate.value, mean_error=candidate.mean_error,
                             sample_count=candidate.sample_count, evaluated_values=candidate.evaluated_values,
                             status="visually_accepted")
