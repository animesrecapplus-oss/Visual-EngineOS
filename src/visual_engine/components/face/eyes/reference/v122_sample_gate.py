from __future__ import annotations

"""V1.22 provenance and dual-sample gate for real pixel calibration.

The gate is intentionally stricter than a numeric calibration fitter. A sample is
eligible only when its semantic review was explicitly approved, its trace was
actually digitized from the exact source bytes, and two distinct candidate/sample
pairs exist. Diagnostic traces remain outside this gate.
"""

from dataclasses import asdict, dataclass
import hashlib
from pathlib import Path
from typing import Any, Iterable

from .digitization import ReferenceSample, ReferenceSource
from .v120_review import V120CandidateReview
from .v121_trace_capture import V121TraceCapture, digitize_v121_capture


@dataclass(frozen=True, slots=True)
class V122DigitizedSample:
    """Pixel sample plus immutable provenance proving which source produced it."""

    candidate_id: str
    sample: ReferenceSample
    source_sha256: str
    source_dimensions: tuple[int, int]
    trace_mode: str

    def __post_init__(self) -> None:
        if not self.candidate_id or not self.sample.sample_id:
            raise ValueError("V1.22 digitized sample requires candidate and sample IDs")
        if len(self.source_sha256) != 64:
            raise ValueError("V1.22 source SHA-256 is required")
        if self.source_dimensions[0] <= 0 or self.source_dimensions[1] <= 0:
            raise ValueError("V1.22 source dimensions must be positive")
        if self.trace_mode not in {"component", "manual"}:
            raise ValueError("V1.22 trace_mode must be component or manual")
        if not self.sample.complete_curve_digitization:
            raise ValueError("V1.22 calibration sample requires complete upper/lower/terminal geometry")


@dataclass(frozen=True, slots=True)
class V122SampleQualification:
    """Audit record for one candidate; it does not create human approval."""

    candidate_id: str
    sample_id: str
    approved: bool
    complete_curve_digitization: bool
    source_sha256: str
    source_dimensions: tuple[int, int]
    trace_mode: str
    blockers: tuple[str, ...] = ()

    @property
    def eligible_for_calibration(self) -> bool:
        return self.approved and self.complete_curve_digitization and not self.blockers


@dataclass(frozen=True, slots=True)
class V122DualSampleGate:
    """Fail-closed handoff state for real source-pixel calibration."""

    source: ReferenceSource
    qualifications: tuple[V122SampleQualification, ...]
    minimum_samples: int = 2

    @property
    def eligible(self) -> bool:
        eligible = [q for q in self.qualifications if q.eligible_for_calibration]
        candidate_ids = {q.candidate_id for q in eligible}
        sample_ids = {q.sample_id for q in eligible}
        return len(eligible) >= self.minimum_samples and len(candidate_ids) >= self.minimum_samples and len(sample_ids) >= self.minimum_samples

    @property
    def status(self) -> str:
        return "READY_FOR_REAL_PIXEL_CALIBRATION" if self.eligible else "BLOCKED_PENDING_TWO_INDEPENDENT_APPROVED_SAMPLES"

    def audit(self) -> dict[str, Any]:
        eligible = [q for q in self.qualifications if q.eligible_for_calibration]
        return {
            "status": self.status,
            "minimum_samples": self.minimum_samples,
            "qualified_count": len(eligible),
            "qualified_candidate_ids": [q.candidate_id for q in eligible],
            "qualified_sample_ids": [q.sample_id for q in eligible],
            "source_sha256": self.source.sha256,
            "source_dimensions": [self.source.width_px, self.source.height_px],
            "nonclaim": "Diagnostic traces and assistant observations are not human approval and cannot satisfy this gate.",
        }


def _source_fingerprint(path: str | Path) -> tuple[str, tuple[int, int]]:
    """Hash exact source bytes and dimensions used by the calibration handoff."""
    path = Path(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    from PIL import Image
    with Image.open(path) as image:
        dimensions = (int(image.width), int(image.height))
    return digest, dimensions


def digitize_v122_sample(source_path: str | Path, review: V120CandidateReview, capture: V121TraceCapture) -> V122DigitizedSample:
    """Perform real V1.21 digitization and attach source provenance immediately."""
    sample = digitize_v121_capture(source_path, review, capture)
    digest, dimensions = _source_fingerprint(source_path)
    mode = "manual" if capture.upper_mode == "manual" else "component"
    return V122DigitizedSample(review.candidate_id, sample, digest, dimensions, mode)


def qualify_sample(
    source_path: str | Path,
    review: V120CandidateReview,
    capture: V121TraceCapture,
    digitized: V122DigitizedSample | None,
) -> V122SampleQualification:
    """Audit one sample and verify the digitized object matches the exact source."""
    digest, dimensions = _source_fingerprint(source_path)
    blockers: list[str] = []
    if not review.is_approved:
        blockers.append("human_review_not_approved")
    if digitized is None:
        blockers.append("pixel_digitization_missing")
    else:
        if digitized.candidate_id != review.candidate_id:
            blockers.append("candidate_id_mismatch")
        if digitized.sample.sample_id != (review.sample_id or ""):
            blockers.append("sample_id_mismatch")
        if digitized.source_sha256 != digest or digitized.source_dimensions != dimensions:
            blockers.append("source_fingerprint_mismatch")
        if digitized.sample.sample_id != capture.candidate_id and not review.sample_id:
            blockers.append("unapproved_sample_identity")
    if capture.candidate_id != review.candidate_id:
        blockers.append("capture_candidate_mismatch")
    return V122SampleQualification(
        candidate_id=review.candidate_id,
        sample_id=review.sample_id or (digitized.sample.sample_id if digitized else ""),
        approved=review.is_approved,
        complete_curve_digitization=bool(digitized and digitized.sample.complete_curve_digitization),
        source_sha256=digest,
        source_dimensions=dimensions,
        trace_mode=(digitized.trace_mode if digitized else "missing"),
        blockers=tuple(dict.fromkeys(blockers)),
    )


def build_dual_sample_gate(
    source_path: str | Path,
    reviews: Iterable[V120CandidateReview],
    captures: Iterable[V121TraceCapture],
    digitized_samples: Iterable[V122DigitizedSample],
    *,
    minimum_samples: int = 2,
) -> V122DualSampleGate:
    """Construct the calibration handoff from explicit reviewed/digitized records."""
    if minimum_samples < 2:
        raise ValueError("V1.22 requires at least two independent samples")
    review_by_id = {r.candidate_id: r for r in reviews}
    capture_by_id = {c.candidate_id: c for c in captures}
    digitized_by_id = {d.candidate_id: d for d in digitized_samples}
    digest, dimensions = _source_fingerprint(source_path)
    source = ReferenceSource(Path(source_path).name, dimensions[0], dimensions[1], digest, True, "V1.22 exact source fingerprint")
    qualifications: list[V122SampleQualification] = []
    for candidate_id in sorted(set(review_by_id) | set(capture_by_id) | set(digitized_by_id)):
        review = review_by_id.get(candidate_id)
        if review is None:
            raise ValueError(f"digitized/capture record has no matching V1.20 review: {candidate_id}")
        capture = capture_by_id.get(candidate_id)
        if capture is None:
            qualifications.append(V122SampleQualification(candidate_id, review.sample_id or "", review.is_approved, False, digest, dimensions, "missing", ("trace_capture_missing",)))
            continue
        q = qualify_sample(source_path, review, capture, digitized_by_id.get(candidate_id))
        qualifications.append(q)
    gate = V122DualSampleGate(source, tuple(qualifications), minimum_samples)
    eligible = [q for q in gate.qualifications if q.eligible_for_calibration]
    if len({q.candidate_id for q in eligible}) != len(eligible):
        raise ValueError("duplicate eligible candidate IDs violate sample independence")
    if len({q.sample_id for q in eligible}) != len(eligible):
        raise ValueError("duplicate eligible sample IDs violate sample independence")
    return gate


def gate_to_json(gate: V122DualSampleGate) -> dict[str, Any]:
    """Serialize the gate for deterministic evidence and later handoff."""
    return {
        "schema_version": "1.22.0",
        "source": asdict(gate.source),
        "qualifications": [asdict(q) for q in gate.qualifications],
        "minimum_samples": gate.minimum_samples,
        "audit": gate.audit(),
    }
