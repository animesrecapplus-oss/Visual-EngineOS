from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import json
import math
from pathlib import Path
from typing import Any

Point = tuple[float, float]


class ReferenceFamily(str, Enum):
    """Style family labels; these are descriptive, not anatomical truths."""

    HUMAN_GENERIC = "human_generic"
    ANIME_STYLIZED = "anime_stylized"
    EXAGGERATED_ARTISTIC = "exaggerated_artistic"
    UNCLASSIFIED = "unclassified"


@dataclass(frozen=True, slots=True)
class ReferenceSource:
    """Provenance for one reference sheet.

    ``pixel_available`` is deliberately explicit. A filename mentioned by an old
    report is not treated as a present pixel source; V1.8 must fail closed rather
    than manufacture control points from a bounding-box table.
    """

    name: str
    width_px: int
    height_px: int
    sha256: str | None = None
    pixel_available: bool = False
    notes: str = ""

    def __post_init__(self) -> None:
        if not self.name or self.width_px <= 0 or self.height_px <= 0:
            raise ValueError("reference source name and positive dimensions are required")
        if self.sha256 is not None and (len(self.sha256) != 64 or any(c not in "0123456789abcdef" for c in self.sha256.lower())):
            raise ValueError("sha256 must be a 64-character hexadecimal digest")


@dataclass(frozen=True, slots=True)
class ReferenceCurve:
    """Pixel-space sampled curve. At least four points are required for tangent extraction."""

    name: str
    points_px: tuple[Point, ...]

    def __post_init__(self) -> None:
        if not self.name or len(self.points_px) < 4:
            raise ValueError("reference curve requires a name and at least four points")
        if any(not all(math.isfinite(v) for v in p) for p in self.points_px):
            raise ValueError("reference curve points must be finite")

    @property
    def tangent_start(self) -> Point:
        a, b = self.points_px[0], self.points_px[1]
        return _unit((b[0] - a[0], b[1] - a[1]))

    @property
    def tangent_end(self) -> Point:
        a, b = self.points_px[-2], self.points_px[-1]
        return _unit((b[0] - a[0], b[1] - a[1]))


@dataclass(frozen=True, slots=True)
class ReferenceSample:
    """One digitized eye sample.

    The six structural regions are optional until the original pixels have been
    supplied. A sample containing only envelope bounds is explicitly incomplete.
    """

    sample_id: str
    family: ReferenceFamily
    upper: ReferenceCurve | None = None
    lower: ReferenceCurve | None = None
    medial_terminal_px: Point | None = None
    lateral_terminal_px: Point | None = None
    caruncle_polygon_px: tuple[Point, ...] = ()
    caruncle_color_rgb: tuple[int, int, int] | None = None
    caruncle_opacity: float | None = None
    epicanthus: ReferenceCurve | None = None
    notes: str = ""
    envelope_width_px: float | None = None
    envelope_height_px: float | None = None

    def __post_init__(self) -> None:
        if self.caruncle_color_rgb is not None and (len(self.caruncle_color_rgb) != 3 or any(not isinstance(v, int) or not 0 <= v <= 255 for v in self.caruncle_color_rgb)):
            raise ValueError("caruncle_color_rgb must contain three integer channels in [0,255]")
        if self.caruncle_opacity is not None and (not math.isfinite(self.caruncle_opacity) or not 0 <= self.caruncle_opacity <= 1):
            raise ValueError("caruncle_opacity must be finite and within [0,1]")

    @property
    def complete_curve_digitization(self) -> bool:
        return all((self.upper, self.lower, self.medial_terminal_px, self.lateral_terminal_px))

    @property
    def complete_medial_detail_digitization(self) -> bool:
        return bool(self.caruncle_polygon_px) or self.epicanthus is not None


def _unit(v: Point) -> Point:
    n = math.hypot(v[0], v[1])
    if n <= 1e-15:
        raise ValueError("degenerate reference tangent")
    return v[0] / n, v[1] / n


@dataclass(frozen=True, slots=True)
class ReferenceDigitizationSet:
    """Versioned reference dataset with an explicit source-completeness gate."""

    schema_version: str
    source: ReferenceSource
    samples: tuple[ReferenceSample, ...] = ()
    provenance: str = ""
    status: str = "pixel_digitization_pending"

    def __post_init__(self) -> None:
        if not self.schema_version or not self.samples:
            raise ValueError("reference dataset requires schema_version and samples")
        if self.status not in {"pixel_digitized", "envelope_only", "pixel_digitization_pending"}:
            raise ValueError("unknown reference digitization status")
        ids = [sample.sample_id for sample in self.samples]
        if len(set(ids)) != len(ids):
            raise ValueError("reference sample ids must be unique")

    @property
    def pixel_digitized_sample_count(self) -> int:
        return sum(sample.complete_curve_digitization for sample in self.samples)

    @property
    def is_pixel_complete(self) -> bool:
        return self.source.pixel_available and self.status == "pixel_digitized" and self.pixel_digitized_sample_count == len(self.samples)


def validate_reference_dataset(dataset: ReferenceDigitizationSet) -> dict[str, Any]:
    """Return audit facts without promoting incomplete data to reference truth."""
    if not isinstance(dataset, ReferenceDigitizationSet):
        raise TypeError("dataset must be ReferenceDigitizationSet")
    return {
        "schema_version": dataset.schema_version,
        "source": dataset.source.name,
        "pixel_available": dataset.source.pixel_available,
        "status": dataset.status,
        "sample_count": len(dataset.samples),
        "pixel_digitized_sample_count": dataset.pixel_digitized_sample_count,
        "pixel_complete": dataset.is_pixel_complete,
        "families": sorted({sample.family.value for sample in dataset.samples}),
        "nonclaim": "No curve/tangent/caruncle truth is inferred when source pixels are unavailable.",
    }


def load_reference_dataset(path: str | Path) -> ReferenceDigitizationSet:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    source = ReferenceSource(**payload["source"])
    samples = []
    for raw in payload["samples"]:
        curves = {}
        for key in ("upper", "lower", "epicanthus"):
            value = raw.get(key)
            curves[key] = ReferenceCurve(value["name"], tuple(tuple(point) for point in value["points_px"])) if value else None
        samples.append(ReferenceSample(
            sample_id=raw["sample_id"],
            family=ReferenceFamily(raw["family"]),
            upper=curves["upper"], lower=curves["lower"],
            medial_terminal_px=tuple(raw["medial_terminal_px"]) if raw.get("medial_terminal_px") else None,
            lateral_terminal_px=tuple(raw["lateral_terminal_px"]) if raw.get("lateral_terminal_px") else None,
            caruncle_polygon_px=tuple(tuple(point) for point in raw.get("caruncle_polygon_px", ())),
            caruncle_color_rgb=tuple(raw["caruncle_color_rgb"]) if raw.get("caruncle_color_rgb") else None,
            caruncle_opacity=raw.get("caruncle_opacity"),
            epicanthus=curves["epicanthus"],
            notes=raw.get("notes", ""),
            envelope_width_px=raw.get("envelope_width_px"), envelope_height_px=raw.get("envelope_height_px"),
        ))
    return ReferenceDigitizationSet(
        schema_version=payload["schema_version"], source=source, samples=tuple(samples),
        provenance=payload.get("provenance", ""), status=payload.get("status", "pixel_digitization_pending"),
    )


def _centroid(points: tuple[Point, ...]) -> Point:
    return (sum(x for x, _ in points) / len(points), sum(y for _, y in points) / len(points))

def _bbox(points: tuple[Point, ...]) -> tuple[float, float, float, float]:
    xs = [p[0] for p in points]; ys = [p[1] for p in points]
    return min(xs), min(ys), max(xs), max(ys)

def measure_reference_sample(sample: ReferenceSample) -> dict[str, Any]:
    """Measure only coordinates actually present in a digitized sample.

    Missing curves/details remain ``None``; no estimate is substituted. Tangent
    angles are derived independently for upper/lower medial/lateral endpoints.
    """
    result: dict[str, Any] = {"sample_id": sample.sample_id, "family": sample.family.value}
    if sample.envelope_width_px and sample.envelope_height_px:
        result["aspect_ratio"] = sample.envelope_width_px / sample.envelope_height_px
    else:
        result["aspect_ratio"] = None
    if sample.upper and sample.lower:
        result["upper_start_tangent_deg"] = math.degrees(math.atan2(*reversed(sample.upper.tangent_start)))
        result["upper_end_tangent_deg"] = math.degrees(math.atan2(*reversed(sample.upper.tangent_end)))
        # Lower is represented in its authored direction; no implicit mirroring is applied.
        result["lower_start_tangent_deg"] = math.degrees(math.atan2(*reversed(sample.lower.tangent_start)))
        result["lower_end_tangent_deg"] = math.degrees(math.atan2(*reversed(sample.lower.tangent_end)))
    else:
        for key in ("upper_start_tangent_deg", "upper_end_tangent_deg", "lower_start_tangent_deg", "lower_end_tangent_deg"):
            result[key] = None
    if sample.caruncle_polygon_px and sample.medial_terminal_px:
        min_x, min_y, max_x, max_y = _bbox(sample.caruncle_polygon_px)
        cx, cy = _centroid(sample.caruncle_polygon_px)
        tx, ty = sample.medial_terminal_px
        result.update({
            "caruncle_width_px": max_x - min_x,
            "caruncle_height_px": max_y - min_y,
            "caruncle_centroid_offset_px": (cx - tx, cy - ty),
        })
    else:
        result.update({"caruncle_width_px": None, "caruncle_height_px": None, "caruncle_centroid_offset_px": None})
    if sample.epicanthus:
        result["epicanthus_start_tangent_deg"] = math.degrees(math.atan2(*reversed(sample.epicanthus.tangent_start)))
        result["epicanthus_end_tangent_deg"] = math.degrees(math.atan2(*reversed(sample.epicanthus.tangent_end)))
    else:
        result["epicanthus_start_tangent_deg"] = None
        result["epicanthus_end_tangent_deg"] = None
    return result
