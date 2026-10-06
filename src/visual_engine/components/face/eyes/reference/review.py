from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
import json
from pathlib import Path
from typing import Any


class ReviewerStatus(str, Enum):
    """Human-review state; ``proposed`` never means approved."""

    PENDING = "pending_human_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    NEEDS_REVISION = "needs_revision"


@dataclass(frozen=True, slots=True)
class CandidateReview:
    """One immutable review decision for one segmentation candidate.

    A sample ID is only legal after approval. This prevents an unreviewed box from
    becoming geometry truth through a loose JSON edit or a partially filled record.
    """

    candidate_id: str
    sample_id: str | None
    region: str
    reviewer_status: ReviewerStatus = ReviewerStatus.PENDING
    reviewer_note: str = ""

    def __post_init__(self) -> None:
        if not self.candidate_id or not self.region:
            raise ValueError("candidate_id and region are required")
        if self.reviewer_status == ReviewerStatus.APPROVED and not self.sample_id:
            raise ValueError("approved candidate requires sample_id")
        if self.reviewer_status != ReviewerStatus.APPROVED and self.sample_id is not None:
            raise ValueError("sample_id is reserved for approved candidates")


@dataclass(frozen=True, slots=True)
class ReviewManifest:
    """Complete, auditable human-review state for a source sheet."""

    schema_version: str
    source_id: str
    source_sha256: str
    candidates: tuple[CandidateReview, ...]

    def __post_init__(self) -> None:
        if not self.schema_version or not self.source_id or len(self.source_sha256) != 64:
            raise ValueError("review manifest requires source identity and SHA-256")
        ids = [c.candidate_id for c in self.candidates]
        if len(ids) != len(set(ids)):
            raise ValueError("candidate IDs must be unique")

    @property
    def approved(self) -> tuple[CandidateReview, ...]:
        return tuple(c for c in self.candidates if c.reviewer_status == ReviewerStatus.APPROVED)

    def validate_complete(self, expected_count: int | None = None) -> None:
        """Fail closed if the manifest does not cover the segmentation candidates."""
        if expected_count is not None and len(self.candidates) != expected_count:
            raise ValueError(f"review manifest covers {len(self.candidates)} candidates, expected {expected_count}")
        if not self.candidates:
            raise ValueError("review manifest cannot be empty")


def review_from_segmentation(payload: dict[str, Any], *, source_sha256: str) -> ReviewManifest:
    """Create a pending manifest; segmentation itself cannot create approvals."""
    candidates = tuple(
        CandidateReview(
            candidate_id=str(item.get("candidate_id") or f"candidate_{index:03d}"),
            sample_id=None,
            region=(f"x={item.get('bbox_px', item)['x']},y={item.get('bbox_px', item)['y']},"
                    f"w={item.get('bbox_px', item)['width']},h={item.get('bbox_px', item)['height']}"),
        )
        for index, item in enumerate(payload.get("candidates", []), 1)
    )
    manifest = ReviewManifest("V1.11-human-review-1", str(payload.get("source_id", "")), source_sha256, candidates)
    manifest.validate_complete(payload.get("candidate_count"))
    return manifest


def save_review_manifest(manifest: ReviewManifest, path: str | Path) -> None:
    """Serialize review decisions deterministically for version control/audit."""
    payload = {
        "schema_version": manifest.schema_version,
        "source_id": manifest.source_id,
        "source_sha256": manifest.source_sha256,
        "candidates": [asdict(c) | {"reviewer_status": c.reviewer_status.value} for c in manifest.candidates],
    }
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_review_manifest(path: str | Path) -> ReviewManifest:
    """Load only explicit reviewer decisions; malformed approval state is rejected."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    candidates = tuple(
        CandidateReview(
            candidate_id=row["candidate_id"], sample_id=row.get("sample_id"),
            region=row["region"], reviewer_status=ReviewerStatus(row["reviewer_status"]),
            reviewer_note=row.get("reviewer_note", ""),
        )
        for row in payload["candidates"]
    )
    return ReviewManifest(payload["schema_version"], payload["source_id"], payload["source_sha256"], candidates)


def render_review_board(source_path: str | Path, segmentation: dict[str, Any], output_path: str | Path) -> dict[str, Any]:
    """Render the source with every candidate ID, without implying approval."""
    from PIL import Image, ImageDraw, ImageFont

    image = Image.open(source_path).convert("RGB")
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    for index, item in enumerate(segmentation.get("candidates", []), 1):
        box = item["bbox_px"]
        x, y = box["x"], box["y"]
        x1, y1 = x + box["width"], y + box["height"]
        draw.rectangle((x, y, x1, y1), outline=(255, 0, 0), width=2)
        label = f"C{index:02d} {item['candidate_id']} PENDING"
        tw = draw.textbbox((0, 0), label, font=font)[2]
        th = draw.textbbox((0, 0), label, font=font)[3]
        ly = max(0, y - th - 3)
        draw.rectangle((x, ly, min(image.width, x + tw + 4), y), fill=(255, 255, 255))
        draw.text((x + 2, ly + 1), label, fill=(200, 0, 0), font=font)
    image.save(output_path, optimize=False)
    return {"output": str(output_path), "width_px": image.width, "height_px": image.height,
            "candidate_count": len(segmentation.get("candidates", [])),
            "status": "pending_human_review"}


def apply_review_decision(manifest: ReviewManifest, candidate_id: str, *, status: ReviewerStatus,
                          sample_id: str | None = None, reviewer_note: str = "") -> ReviewManifest:
    """Return a new manifest with one explicit reviewer decision.

    The function is intentionally immutable: a review history can therefore be
    diffed in version control and a rejected/changed decision cannot mutate an
    already-created ``ReferenceSample`` in place.
    """
    if status == ReviewerStatus.APPROVED and not sample_id:
        raise ValueError("approved candidate requires sample_id")
    if status != ReviewerStatus.APPROVED and sample_id is not None:
        raise ValueError("sample_id is only valid for approved candidates")
    found = False
    updated = []
    for candidate in manifest.candidates:
        if candidate.candidate_id == candidate_id:
            found = True
            updated.append(CandidateReview(candidate_id, sample_id, candidate.region, status, reviewer_note))
        else:
            updated.append(candidate)
    if not found:
        raise KeyError(f"unknown candidate_id: {candidate_id}")
    return ReviewManifest(manifest.schema_version, manifest.source_id, manifest.source_sha256, tuple(updated))
