from __future__ import annotations

from dataclasses import dataclass
import math
from pathlib import Path
from typing import Any

from .digitization import ReferenceCurve, ReferenceFamily, ReferenceSample


@dataclass(frozen=True, slots=True)
class TraceRegion:
    """A human-approved crop within a reference sheet.

    Segmentation never creates approval. ``approved`` must be supplied by a
    reviewer after looking at the labelled source crop.
    """

    x: int
    y: int
    width: int
    height: int
    sample_id: str
    approved: bool = False

    def __post_init__(self) -> None:
        if min(self.x, self.y) < 0 or min(self.width, self.height) <= 0 or not self.sample_id:
            raise ValueError("invalid trace region")


def _centerline_points(labels, label: int, *, offset_x: int, offset_y: int) -> list[tuple[float, float]]:
    """Return an orientation-independent centerline proposal for one ink stroke.

    PCA binning is used instead of one-point-per-image-x. It survives vertical and
    diagonal eye studies without assuming that the reference is front-facing.
    It is still a *proposal*: a reviewer must inspect the resulting polyline.
    """
    import numpy as np

    ys, xs = np.where(labels == label)
    if len(xs) < 4:
        return []
    points = np.column_stack((xs.astype(float), ys.astype(float)))
    centered = points - points.mean(axis=0)
    covariance = centered.T @ centered
    _, vectors = np.linalg.eigh(covariance)
    axis = vectors[:, int(np.argmax(np.linalg.eigvalsh(covariance)))]
    if axis[0] < 0 or (abs(axis[0]) < 1e-12 and axis[1] < 0):
        axis = -axis
    normal = np.array([-axis[1], axis[0]])
    along = centered @ axis
    span = float(along.max() - along.min())
    bins = max(4, min(256, int(round(span))))
    edges = np.linspace(along.min(), along.max(), bins + 1)
    result: list[tuple[float, float]] = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        chosen = points[(along >= lo) & (along <= hi if hi == edges[-1] else along < hi)]
        if len(chosen) == 0:
            continue
        # Median perpendicular coordinate is robust to stroke thickness and small
        # anti-aliasing islands while retaining dense source-pixel sampling.
        center = chosen.mean(axis=0)
        perp = chosen - center
        offset = float(np.median(perp @ normal))
        p = center + offset * normal
        result.append((float(p[0] + offset_x), float(p[1] + offset_y)))
    return result


def trace_component_candidates(path: str | Path, region: TraceRegion) -> dict[str, Any]:
    """Return dark-ink component candidates for manual upper/lower selection.

    Candidate IDs are stable within the crop. The trace is orientation-independent
    and remains in source pixels. No component is auto-labelled as anatomy.
    """
    import cv2
    import numpy as np
    from PIL import Image

    image = np.asarray(Image.open(path).convert("RGB"))
    h, w = image.shape[:2]
    x1, y1 = region.x + region.width, region.y + region.height
    if x1 > w or y1 > h:
        raise ValueError("trace region lies outside reference image")
    crop = image[region.y:y1, region.x:x1]
    mx, mn = crop.max(axis=2), crop.min(axis=2)
    mask = ((mx < 105) & ((mx.astype(np.int16) - mn.astype(np.int16)) < 35)).astype(np.uint8) * 255
    # Do not open the mask here: a thin anti-aliased diagonal can be split by a
    # 3x3 opening, destroying the very continuity that the digitizer must measure.
    count, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, 8)
    candidates: list[dict[str, Any]] = []
    for label in range(1, count):
        x, y, bw, bh, area = [int(v) for v in stats[label]]
        if area < 6 or bw < max(3, region.width // 30):
            continue
        points = _centerline_points(labels, label, offset_x=region.x, offset_y=region.y)
        if len(points) < 4:
            continue
        candidates.append({
            "candidate_id": f"ink_{label:03d}",
            "bbox_px": {"x": region.x + x, "y": region.y + y, "width": bw, "height": bh},
            "area_px": area,
            "centroid_px": (region.x + float(centroids[label][0]), region.y + float(centroids[label][1])),
            "points_px": points,
            "trace_method": "pca_perpendicular_median",
        })
    candidates.sort(key=lambda item: (item["bbox_px"]["y"], item["bbox_px"]["x"], item["candidate_id"]))
    return {"sample_id": region.sample_id, "candidate_count": len(candidates), "candidates": candidates,
            "status": "manual_component_selection_required",
            "nonclaim": "No candidate is upper/lower anatomy until explicitly selected by a human reviewer."}


def digitize_approved_eye(
    path: str | Path, region: TraceRegion, *, family: ReferenceFamily,
    upper_candidate_id: str, lower_candidate_id: str,
    inner_terminal_px: tuple[float, float] | None = None, outer_terminal_px: tuple[float, float] | None = None,
    eye_side: str = "single", reviewer_note: str = "",
    medial_terminal_px: tuple[float, float] | None = None, lateral_terminal_px: tuple[float, float] | None = None,
    caruncle_polygon_px: tuple[tuple[float, float], ...] = (),
    caruncle_color_rgb: tuple[int, int, int] | None = None,
    caruncle_opacity: float | None = None,
    epicanthus_candidate_id: str | None = None,
    epicanthus_status: str = "unknown",
) -> ReferenceSample:
    """Promote only a reviewer-approved eye and preserve every manual choice.

    Inner/outer are semantic ocular terminals. For a normal human eye, inner is
    medial and outer is lateral; the side argument is recorded for downstream
    validation. Caruncle/epicanthus are opt-in and never inferred from contour ink.
    """
    if not region.approved:
        raise ValueError("reference region must be explicitly approved before digitization")
    # V1.10 keyword names remain accepted as a compatibility shim. The canonical
    # V1.11 vocabulary is inner/outer; both resolve to the same semantic roles.
    inner_terminal_px = inner_terminal_px if inner_terminal_px is not None else medial_terminal_px
    outer_terminal_px = outer_terminal_px if outer_terminal_px is not None else lateral_terminal_px
    if inner_terminal_px is None or outer_terminal_px is None:
        raise ValueError("inner and outer terminal coordinates are required")
    if eye_side not in {"image_left", "image_right", "single"}:
        raise ValueError("eye_side must be image_left, image_right or single")
    if epicanthus_status not in {"present", "absent", "unknown"}:
        raise ValueError("epicanthus_status must be present, absent or unknown")
    data = trace_component_candidates(path, region)
    by_id = {item["candidate_id"]: item for item in data["candidates"]}
    if upper_candidate_id not in by_id or lower_candidate_id not in by_id:
        raise ValueError("selected trace component is not present in the approved region")
    if upper_candidate_id == lower_candidate_id:
        raise ValueError("upper and lower trace components must be independent")
    def orient(points: list[tuple[float, float]]) -> tuple[tuple[float, float], ...]:
        # Tracing has no anatomical direction. Make start == inner terminal so
        # endpoint measurements have one explicit convention across all samples.
        if len(points) < 4:
            raise ValueError("selected trace is too short for calibration")
        start_d = math.dist(points[0], inner_terminal_px)
        end_d = math.dist(points[-1], inner_terminal_px)
        if abs(start_d - end_d) <= 1e-12:
            raise ValueError("selected trace direction is ambiguous relative to inner terminal")
        return tuple(points if start_d < end_d else reversed(points))

    upper_points = orient(by_id[upper_candidate_id]["points_px"])
    lower_points = orient(by_id[lower_candidate_id]["points_px"])
    epicanthus = None
    if epicanthus_status == "present":
        if not epicanthus_candidate_id or epicanthus_candidate_id not in by_id:
            raise ValueError("present epicanthus requires an explicitly selected trace component")
        epicanthus = ReferenceCurve("epicanthus", tuple(tuple(p) for p in by_id[epicanthus_candidate_id]["points_px"]))
    elif epicanthus_candidate_id is not None:
        raise ValueError("epicanthus candidate may be supplied only when status is present")
    audit = (
        f"selected upper={upper_candidate_id}, lower={lower_candidate_id}; "
        f"inner_terminal={inner_terminal_px}, outer_terminal={outer_terminal_px}; "
        f"eye_side={eye_side}; epicanthus_status={epicanthus_status}; source={Path(path).name}"
    )
    return ReferenceSample(
        sample_id=region.sample_id, family=family,
        upper=ReferenceCurve("upper", upper_points),
        lower=ReferenceCurve("lower", lower_points),
        medial_terminal_px=inner_terminal_px, lateral_terminal_px=outer_terminal_px,
        caruncle_polygon_px=caruncle_polygon_px, caruncle_color_rgb=caruncle_color_rgb,
        caruncle_opacity=caruncle_opacity, epicanthus=epicanthus,
        notes=(reviewer_note + " | " if reviewer_note else "") + audit,
    )
