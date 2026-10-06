from __future__ import annotations

"""V1.21 trace-capture layer for difficult source-pixel eye studies.

V1.20 correctly refused to infer anatomy, but its component-only trace path has a
real blind spot: an upper and lower lid can be one connected ink component, and a
segmentation box can contain a whole face panel. V1.21 keeps the V1.20 semantic
approval gate and adds an explicit trace-region + manual-polyline path.

Manual points are source-pixel coordinates. They are reviewer input, not machine-
inferred anatomy. The optional component path remains available for easy cases.
"""

from dataclasses import asdict, dataclass
import math
from pathlib import Path
from typing import Any, Literal

from .digitization import ReferenceCurve, ReferenceSample
from .pixel_trace import TraceRegion, digitize_approved_eye, trace_component_candidates
from .v120_review import V120CandidateReview, MANUAL_LOWER_TRACE_ID, MANUAL_UPPER_TRACE_ID

TraceMode = Literal["component", "manual"]


@dataclass(frozen=True, slots=True)
class TraceRegionV121:
    """Reviewer-selected crop; the original V1.20 source box remains provenance."""

    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if min(self.x, self.y) < 0 or min(self.width, self.height) <= 0:
            raise ValueError("invalid V1.21 trace region")


@dataclass(frozen=True, slots=True)
class ManualPolylineV121:
    """Dense source-pixel polyline captured by a reviewer."""

    points_px: tuple[tuple[float, float], ...]
    method: str = "manual_source_pixel_trace"

    def __post_init__(self) -> None:
        if len(self.points_px) < 4:
            raise ValueError("manual trace requires at least four points")
        if any(not all(math.isfinite(v) for v in point) for point in self.points_px):
            raise ValueError("manual trace points must be finite")
        if any(a == b for a, b in zip(self.points_px, self.points_px[1:])):
            raise ValueError("manual trace cannot contain consecutive duplicate points")
        if not self.method:
            raise ValueError("manual trace method is required")


@dataclass(frozen=True, slots=True)
class V121TraceCapture:
    """Trace acquisition decision attached to an already reviewed V1.20 eye."""

    candidate_id: str
    trace_region: TraceRegionV121
    upper_mode: TraceMode
    lower_mode: TraceMode
    upper_component_id: str | None = None
    lower_component_id: str | None = None
    upper_manual: ManualPolylineV121 | None = None
    lower_manual: ManualPolylineV121 | None = None
    epicanthus_mode: TraceMode | None = None
    epicanthus_component_id: str | None = None
    epicanthus_manual: ManualPolylineV121 | None = None

    def __post_init__(self) -> None:
        if not self.candidate_id:
            raise ValueError("candidate_id is required")
        self._validate_pair("upper", self.upper_mode, self.upper_component_id, self.upper_manual)
        self._validate_pair("lower", self.lower_mode, self.lower_component_id, self.lower_manual)
        if self.epicanthus_mode is not None:
            self._validate_pair("epicanthus", self.epicanthus_mode, self.epicanthus_component_id, self.epicanthus_manual)

    @staticmethod
    def _validate_pair(name: str, mode: TraceMode, component_id: str | None, manual: ManualPolylineV121 | None) -> None:
        if mode not in {"component", "manual"}:
            raise ValueError(f"{name}_mode must be component or manual")
        if mode == "component" and (not component_id or manual is not None):
            raise ValueError(f"{name} component mode requires only component_id")
        if mode == "manual" and (manual is None or component_id is not None):
            raise ValueError(f"{name} manual mode requires only manual points")


def trace_capture_to_json(capture: V121TraceCapture) -> dict[str, Any]:
    """Serialize a trace capture without losing raw reviewer points."""
    return asdict(capture)


def load_trace_capture(payload: dict[str, Any]) -> V121TraceCapture:
    """Load a capture and validate every mode/point invariant before use."""
    def polyline(value: Any) -> ManualPolylineV121 | None:
        if value is None:
            return None
        return ManualPolylineV121(tuple(tuple(p) for p in value["points_px"]), value.get("method", "manual_source_pixel_trace"))

    return V121TraceCapture(
        candidate_id=str(payload["candidate_id"]),
        trace_region=TraceRegionV121(**payload["trace_region"]),
        upper_mode=payload["upper_mode"], lower_mode=payload["lower_mode"],
        upper_component_id=payload.get("upper_component_id"), lower_component_id=payload.get("lower_component_id"),
        upper_manual=polyline(payload.get("upper_manual")), lower_manual=polyline(payload.get("lower_manual")),
        epicanthus_mode=payload.get("epicanthus_mode"),
        epicanthus_component_id=payload.get("epicanthus_component_id"), epicanthus_manual=polyline(payload.get("epicanthus_manual")),
    )


def _manual_sample(review: V120CandidateReview, capture: V121TraceCapture) -> ReferenceSample:
    """Build source geometry directly from reviewer pixel traces."""
    def oriented(polyline: ManualPolylineV121, inner: tuple[float, float]) -> tuple[tuple[float, float], ...]:
        points = polyline.points_px
        d0 = math.dist(points[0], inner)
        d1 = math.dist(points[-1], inner)
        if abs(d0 - d1) <= 1e-12:
            raise ValueError("manual trace direction is ambiguous relative to medial terminal")
        return points if d0 < d1 else tuple(reversed(points))

    if not review.medial_terminal_px or not review.lateral_terminal_px or not review.sample_id:
        raise ValueError("approved V1.20 review must contain terminals and sample_id")
    upper = capture.upper_manual
    lower = capture.lower_manual
    assert upper is not None and lower is not None
    epicanthus = None
    if review.epicanthus_status.value == "present":
        if capture.epicanthus_manual is None:
            raise ValueError("present epicanthus requires a manual trace when epicanthus_mode=manual")
        epicanthus = ReferenceCurve("epicanthus", capture.epicanthus_manual.points_px)
    return ReferenceSample(
        sample_id=review.sample_id, family=review.family,
        upper=ReferenceCurve("upper", oriented(upper, review.medial_terminal_px)),
        lower=ReferenceCurve("lower", oriented(lower, review.medial_terminal_px)),
        medial_terminal_px=review.medial_terminal_px, lateral_terminal_px=review.lateral_terminal_px,
        caruncle_polygon_px=review.caruncle_polygon_px, epicanthus=epicanthus,
        notes=(review.reviewer_note + " | " if review.reviewer_note else "") +
              "V1.21 manual source-pixel traces; no curve fit substituted.",
    )


def digitize_v121_capture(source_path: str | Path, review: V120CandidateReview, capture: V121TraceCapture) -> ReferenceSample:
    """Digitize one approved V1.20 eye using component or explicit pixel traces.

    Component mode delegates to the V1.20 pixel tracer. Manual mode deliberately
    does not re-detect the contour: the reviewer supplied the source coordinates.
    """
    if not review.is_approved:
        raise ValueError("V1.21 trace capture requires an explicitly approved V1.20 review")
    if capture.candidate_id != review.candidate_id:
        raise ValueError("trace capture candidate_id does not match review")
    if capture.upper_mode == "manual" or capture.lower_mode == "manual":
        if review.upper_candidate_id != MANUAL_UPPER_TRACE_ID or review.lower_candidate_id != MANUAL_LOWER_TRACE_ID:
            raise ValueError("manual V1.21 capture requires the explicit V1.21 reserved trace selections")
        if capture.upper_mode != "manual" or capture.lower_mode != "manual":
            raise ValueError("mixed component/manual upper/lower capture is not supported; choose both explicitly")
        return _manual_sample(review, capture)
    region = TraceRegion(capture.trace_region.x, capture.trace_region.y, capture.trace_region.width,
                         capture.trace_region.height, review.sample_id or "", approved=True)
    # Component IDs are resolved inside the reviewer-selected trace region, not the
    # original contextual segmentation box. This fixes V1.20's promised-but-missing
    # smaller-region capability without changing the original provenance box.
    return digitize_approved_eye(
        source_path, region, family=review.family,
        upper_candidate_id=capture.upper_component_id or "", lower_candidate_id=capture.lower_component_id or "",
        medial_terminal_px=review.medial_terminal_px, lateral_terminal_px=review.lateral_terminal_px,
        eye_side=review.eye_side or "single", reviewer_note=review.reviewer_note,
        caruncle_polygon_px=review.caruncle_polygon_px,
        epicanthus_candidate_id=capture.epicanthus_component_id,
        epicanthus_status=review.epicanthus_status.value,
    )


def inspect_trace_components(source_path: str | Path, region: TraceRegionV121, sample_id: str = "inspect") -> dict[str, Any]:
    """Expose component proposals for review; never labels upper/lower anatomy."""
    return trace_component_candidates(source_path, TraceRegion(region.x, region.y, region.width, region.height, sample_id))
