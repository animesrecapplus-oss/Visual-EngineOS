from __future__ import annotations

"""V1.20 explicit human-review and source-pixel digitization contracts.

Machine segmentation never becomes semantic truth without an explicit reviewer
decision.  This module stores those decisions and delegates approved traces to the
existing source-pixel digitizer.
"""

from dataclasses import asdict, dataclass
from enum import Enum
import json
from pathlib import Path
from typing import Any

from .digitization import ReferenceFamily, ReferenceSample
from .pixel_trace import TraceRegion, digitize_approved_eye
from .review import ReviewerStatus

class EyeIdentification(str, Enum):
    YES = "yes"
    NO = "no"
    UNCERTAIN = "uncertain"

class CaruncleReview(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    UNKNOWN = "unknown"

MANUAL_UPPER_TRACE_ID = "__manual_upper_trace__"
MANUAL_LOWER_TRACE_ID = "__manual_lower_trace__"

class EpicanthusReview(str, Enum):
    PRESENT = "present"
    ABSENT = "absent"
    UNKNOWN = "unknown"

@dataclass(frozen=True, slots=True)
class TraceRegionV120:
    """Exact source-pixel crop selected by the reviewer for one eye study.

    The region may equal the V1.10 segmentation box or be a smaller manual crop
    when a segmentation component contains a contextual face panel.
    """

    x: int
    y: int
    width: int
    height: int

    def __post_init__(self) -> None:
        if min(self.x, self.y) < 0 or min(self.width, self.height) <= 0:
            raise ValueError("invalid V1.20 trace region")

@dataclass(frozen=True, slots=True)
class V120CandidateReview:
    """Complete human decision record for one segmentation candidate.

    An approved record cannot omit any semantic decision needed by V1.20.  In
    particular, ``unknown`` is different from ``absent`` for caruncle/epicanthus.
    """

    candidate_id: str
    source_bbox: TraceRegionV120
    eye_identification: EyeIdentification = EyeIdentification.UNCERTAIN
    eye_side: str | None = None
    upper_candidate_id: str | None = None
    lower_candidate_id: str | None = None
    medial_terminal_px: tuple[float, float] | None = None
    lateral_terminal_px: tuple[float, float] | None = None
    caruncle_status: CaruncleReview = CaruncleReview.UNKNOWN
    caruncle_polygon_px: tuple[tuple[float, float], ...] = ()
    epicanthus_status: EpicanthusReview = EpicanthusReview.UNKNOWN
    epicanthus_candidate_id: str | None = None
    family: ReferenceFamily = ReferenceFamily.UNCLASSIFIED
    sample_id: str | None = None
    reviewer_status: ReviewerStatus = ReviewerStatus.PENDING
    reviewer_note: str = ""

    def __post_init__(self) -> None:
        if not self.candidate_id:
            raise ValueError("candidate_id is required")
        if self.eye_side is not None and self.eye_side not in {"image_left", "image_right", "single"}:
            raise ValueError("eye_side must be image_left, image_right or single")
        if self.reviewer_status == ReviewerStatus.APPROVED:
            self._validate_approval()
        elif self.sample_id is not None:
            raise ValueError("sample_id is reserved for approved V1.20 records")

    def _validate_approval(self) -> None:
        if self.eye_identification != EyeIdentification.YES:
            raise ValueError("approved V1.20 record must explicitly identify a real eye")
        if self.eye_side not in {"image_left", "image_right", "single"}:
            raise ValueError("approved V1.20 record requires explicit eye_side")
        if not self.upper_candidate_id or not self.lower_candidate_id:
            raise ValueError("approved V1.20 record requires explicit upper and lower trace selections")
        manual_pair = (self.upper_candidate_id == MANUAL_UPPER_TRACE_ID and self.lower_candidate_id == MANUAL_LOWER_TRACE_ID)
        if self.upper_candidate_id == self.lower_candidate_id:
            raise ValueError("upper and lower trace selections must be independent")
        if self.upper_candidate_id.startswith("__manual") or self.lower_candidate_id.startswith("__manual"):
            if not manual_pair:
                raise ValueError("manual trace selection requires both reserved upper/lower IDs")
        if self.medial_terminal_px is None or self.lateral_terminal_px is None:
            raise ValueError("approved V1.20 record requires explicit medial and lateral terminals")
        if self.medial_terminal_px == self.lateral_terminal_px:
            raise ValueError("medial and lateral terminals must differ")
        if self.caruncle_status == CaruncleReview.PRESENT and len(self.caruncle_polygon_px) < 3:
            raise ValueError("present caruncle requires an explicit polygon")
        if self.caruncle_status != CaruncleReview.PRESENT and self.caruncle_polygon_px:
            raise ValueError("caruncle polygon is allowed only when status is present")
        if self.epicanthus_status == EpicanthusReview.PRESENT and not self.epicanthus_candidate_id:
            raise ValueError("present epicanthus requires an explicit trace candidate")
        if self.epicanthus_status != EpicanthusReview.PRESENT and self.epicanthus_candidate_id is not None:
            raise ValueError("epicanthus candidate is allowed only when status is present")
        if not self.sample_id:
            raise ValueError("approved V1.20 record requires sample_id")

    @property
    def is_approved(self) -> bool:
        return self.reviewer_status == ReviewerStatus.APPROVED

def _trace_region_from_candidate(row: dict[str, Any]) -> TraceRegionV120:
    box = row.get("bbox_px") or row
    return TraceRegionV120(int(box["x"]), int(box["y"]), int(box["width"]), int(box["height"]))

def create_pending_v120_manifest(segmentation: dict[str, Any], *, source_id: str, source_sha256: str) -> dict[str, Any]:
    """Create a complete, explicitly pending V1.20 review template."""
    candidates = []
    for index, row in enumerate(segmentation.get("candidates", []), 1):
        candidate_id = str(row.get("candidate_id") or f"candidate_{index:03d}")
        box = _trace_region_from_candidate(row)
        candidates.append({
            "candidate_id": candidate_id,
            "source_bbox": asdict(box),
            "eye_identification": EyeIdentification.UNCERTAIN.value,
            "eye_side": None,
            "upper_candidate_id": None,
            "lower_candidate_id": None,
            "medial_terminal_px": None,
            "lateral_terminal_px": None,
            "caruncle_status": CaruncleReview.UNKNOWN.value,
            "caruncle_polygon_px": [],
            "epicanthus_status": EpicanthusReview.UNKNOWN.value,
            "epicanthus_candidate_id": None,
            "family": ReferenceFamily.UNCLASSIFIED.value,
            "sample_id": None,
            "reviewer_status": ReviewerStatus.PENDING.value,
            "reviewer_note": "",
        })
    if len(candidates) != int(segmentation.get("candidate_count", len(candidates))):
        raise ValueError("segmentation candidate count is internally inconsistent")
    return {
        "schema_version": "V1.20-human-review-1",
        "source_id": source_id,
        "source_sha256": source_sha256,
        "candidate_count": len(candidates),
        "approved_count": 0,
        "candidates": candidates,
        "status": "pending_human_review",
        "nonclaim": "No candidate is an eye, no terminal is semantic, and no family/detail status is truth until explicitly reviewed.",
    }

def _enum_value(value: Any, enum_type: type[Enum]) -> Any:
    return value if isinstance(value, enum_type) else enum_type(value)

def load_v120_reviews(path: str | Path) -> tuple[V120CandidateReview, ...]:
    """Load and validate reviewer decisions; malformed approvals fail closed."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if payload.get("schema_version") != "V1.20-human-review-1":
        raise ValueError("not a V1.20 human-review manifest")
    records: list[V120CandidateReview] = []
    seen_ids: set[str] = set()
    seen_samples: set[str] = set()
    for row in payload.get("candidates", []):
        record = V120CandidateReview(
            candidate_id=row["candidate_id"],
            source_bbox=TraceRegionV120(**row["source_bbox"]),
            eye_identification=_enum_value(row.get("eye_identification", "uncertain"), EyeIdentification),
            eye_side=row.get("eye_side"),
            upper_candidate_id=row.get("upper_candidate_id"),
            lower_candidate_id=row.get("lower_candidate_id"),
            medial_terminal_px=tuple(row["medial_terminal_px"]) if row.get("medial_terminal_px") else None,
            lateral_terminal_px=tuple(row["lateral_terminal_px"]) if row.get("lateral_terminal_px") else None,
            caruncle_status=_enum_value(row.get("caruncle_status", "unknown"), CaruncleReview),
            caruncle_polygon_px=tuple(tuple(p) for p in row.get("caruncle_polygon_px", [])),
            epicanthus_status=_enum_value(row.get("epicanthus_status", "unknown"), EpicanthusReview),
            epicanthus_candidate_id=row.get("epicanthus_candidate_id"),
            family=ReferenceFamily(row.get("family", ReferenceFamily.UNCLASSIFIED.value)),
            sample_id=row.get("sample_id"),
            reviewer_status=_enum_value(row.get("reviewer_status", ReviewerStatus.PENDING.value), ReviewerStatus),
            reviewer_note=row.get("reviewer_note", ""),
        )
        if record.candidate_id in seen_ids:
            raise ValueError(f"duplicate candidate_id: {record.candidate_id}")
        seen_ids.add(record.candidate_id)
        if record.sample_id:
            if record.sample_id in seen_samples:
                raise ValueError(f"duplicate approved sample_id: {record.sample_id}")
            seen_samples.add(record.sample_id)
        records.append(record)
    if not records:
        raise ValueError("V1.20 review manifest cannot be empty")
    expected = payload.get("candidate_count")
    if expected is not None and len(records) != int(expected):
        raise ValueError("V1.20 review manifest does not cover every candidate")
    return tuple(records)

def approved_v120_records(path: str | Path) -> tuple[V120CandidateReview, ...]:
    """Return only explicit approvals; pending/rejected records never leak into calibration."""
    records = load_v120_reviews(path)
    return tuple(record for record in records if record.is_approved)

def digitize_v120_review(source_path: str | Path, review: V120CandidateReview) -> ReferenceSample:
    """Turn one *approved* V1.20 decision into source-pixel geometry.

    The actual contour traces still come from the original source pixels through
    ``digitize_approved_eye``. The review record supplies the semantic labels that
    segmentation intentionally cannot infer.
    """
    if not review.is_approved:
        raise ValueError("only an explicitly approved V1.20 record can be digitized")
    region = TraceRegion(
        review.source_bbox.x, review.source_bbox.y,
        review.source_bbox.width, review.source_bbox.height,
        review.sample_id or "",
        approved=True,
    )
    return digitize_approved_eye(
        source_path, region,
        family=review.family,
        upper_candidate_id=review.upper_candidate_id or "",
        lower_candidate_id=review.lower_candidate_id or "",
        medial_terminal_px=review.medial_terminal_px,
        lateral_terminal_px=review.lateral_terminal_px,
        eye_side=review.eye_side or "single",
        reviewer_note=review.reviewer_note,
        caruncle_polygon_px=review.caruncle_polygon_px,
        epicanthus_candidate_id=review.epicanthus_candidate_id,
        epicanthus_status=review.epicanthus_status.value,
    )

