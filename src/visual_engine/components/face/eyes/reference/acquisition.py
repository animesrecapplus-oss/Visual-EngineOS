from __future__ import annotations

from dataclasses import dataclass, asdict
import hashlib
import json
from pathlib import Path
from statistics import median
from typing import Any
import shutil
from urllib.request import Request, urlopen


@dataclass(frozen=True, slots=True)
class ReferenceAcquisitionRecord:
    """Auditable acquisition state for one external reference source.

    A candidate URL is never accepted as the authoritative pixel source until
    both dimensions and SHA-256 match the recorded source contract. This prevents
    a resized web preview from silently replacing the original sheet.
    """

    source_id: str
    expected_name: str
    expected_sha256: str | None
    expected_width_px: int | None
    expected_height_px: int | None
    expected_format: str | None = None
    expected_orientation: str | None = None
    candidate_url: str | None = None
    status: str = "missing"
    local_path: str | None = None
    actual_sha256: str | None = None
    actual_width_px: int | None = None
    actual_height_px: int | None = None
    actual_format: str | None = None
    actual_orientation: str | None = None
    crop_status: str = "unknown"
    notes: str = ""


def sha256_file(path: str | Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def inspect_image_metadata(path: str | Path) -> dict[str, Any]:
    """Inspect file facts without interpreting pixels as ocular geometry.

    A standalone file cannot prove absence of an upstream crop. ``crop_status``
    therefore remains ``unknown`` unless provenance supplies an expected canvas.
    """
    from PIL import Image
    p = Path(path)
    with Image.open(p) as im:
        width, height = im.size
        fmt = (im.format or p.suffix.lstrip(".")).upper()
        exif = im.getexif()
        orientation_value = exif.get(274)
    orientation = "normal" if orientation_value in (None, 1) else f"exif_{orientation_value}"
    return {"width_px": width, "height_px": height, "sha256": sha256_file(p), "format": fmt, "orientation": orientation}


def inspect_image_file(path: str | Path) -> tuple[int, int, str]:
    """Backward-compatible dimensions/hash inspection."""
    meta = inspect_image_metadata(path)
    return meta["width_px"], meta["height_px"], meta["sha256"]


def verify_reference_file(record: ReferenceAcquisitionRecord, path: str | Path) -> ReferenceAcquisitionRecord:
    """Fail closed when a supplied image is not the exact recorded source."""
    meta = inspect_image_metadata(path)
    width, height, digest = meta["width_px"], meta["height_px"], meta["sha256"]
    notes = []
    if record.expected_sha256 and digest.lower() != record.expected_sha256.lower():
        notes.append("sha256 mismatch")
    if record.expected_width_px and width != record.expected_width_px:
        notes.append(f"width mismatch: {width} != {record.expected_width_px}")
    if record.expected_height_px and height != record.expected_height_px:
        notes.append(f"height mismatch: {height} != {record.expected_height_px}")
    if record.expected_format and meta["format"].lower() != record.expected_format.lower():
        notes.append(f"format mismatch: {meta['format']} != {record.expected_format}")
    if record.expected_orientation and meta["orientation"] != record.expected_orientation:
        notes.append(f"orientation mismatch: {meta['orientation']} != {record.expected_orientation}")
    status = "verified" if not notes else "rejected"
    return ReferenceAcquisitionRecord(
        **{**asdict(record), "status": status, "local_path": str(Path(path)),
           "actual_sha256": digest, "actual_width_px": width,
           "actual_height_px": height, "actual_format": meta["format"],
           "actual_orientation": meta["orientation"], "crop_status": "unknown",
           "notes": "; ".join(notes) or "exact source facts verified; crop absence remains provenance-gated"}
    )


def acquire_reference_file(record: ReferenceAcquisitionRecord, destination: str | Path, *, timeout: float = 20.0) -> ReferenceAcquisitionRecord:
    """Download a candidate only to a temporary path, then verify before promotion."""
    if not record.candidate_url:
        return ReferenceAcquisitionRecord(**{**asdict(record), "status": "missing", "notes": "no candidate URL"})
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".download")
    request = Request(record.candidate_url, headers={"User-Agent": "VisualEngineReferenceAcquirer/1.0"})
    try:
        with urlopen(request, timeout=timeout) as response, temporary.open("wb") as out:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                out.write(chunk)
        checked = verify_reference_file(record, temporary)
        if checked.status != "verified":
            temporary.unlink(missing_ok=True)
            return checked
        temporary.replace(destination)
        return verify_reference_file(record, destination)
    except Exception as exc:
        temporary.unlink(missing_ok=True)
        return ReferenceAcquisitionRecord(**{**asdict(record), "status": "acquisition_failed", "notes": f"{type(exc).__name__}: {exc}"})


def preserve_reference_file(source: str | Path, destination: str | Path) -> ReferenceAcquisitionRecord:
    """Copy exact bytes once; refuse silent overwrite of a different source.

    The repository stores the verified byte stream plus its digest. OS-level
    read-only permissions are not treated as the integrity mechanism because ZIP
    and source-control transports can normalize permissions; digest comparison is.
    """
    source = Path(source); destination = Path(destination)
    try:
        meta = inspect_image_metadata(source)
    except Exception as exc:
        raise ValueError(f"source reference is not a readable image: {exc}") from exc
    if destination.exists():
        if sha256_file(destination) != meta["sha256"]:
            raise ValueError("immutable reference destination already contains different bytes")
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, destination)
    return ReferenceAcquisitionRecord(
        source_id="preserved_local_reference", expected_name=source.name,
        expected_sha256=meta["sha256"], expected_width_px=meta["width_px"],
        expected_height_px=meta["height_px"], expected_format=meta["format"],
        expected_orientation=meta["orientation"], status="verified",
        local_path=str(destination), actual_sha256=meta["sha256"],
        actual_width_px=meta["width_px"], actual_height_px=meta["height_px"],
        actual_format=meta["format"], actual_orientation=meta["orientation"], crop_status="unknown",
        notes="byte-preserved user-supplied source; upstream crop absence is not inferable from the file alone"
    )

def segment_reference_sheet(path: str | Path, *, min_component_area_fraction: float = 0.00002) -> dict[str, Any]:
    """Produce candidate foreground boxes without assuming a fixed grid.

    This is deliberately a *segmentation proposal*, not automatic truth. The
    algorithm estimates the border background, extracts foreground ink by colour
    distance, dilates nearby strokes so one eye's disconnected line-art can form a
    candidate component, and returns auditable boxes. Manual/visual review remains
    mandatory before a box becomes a ReferenceSample.
    """
    import cv2
    import numpy as np
    from PIL import Image

    image = np.asarray(Image.open(path).convert("RGB"))
    h, w = image.shape[:2]
    border = np.concatenate((image[0, :, :], image[-1, :, :], image[:, 0, :], image[:, -1, :]), axis=0)
    bg = np.median(border, axis=0)
    distance = np.max(np.abs(image.astype(np.int16) - bg.astype(np.int16)), axis=2)
    mask = (distance > 24).astype(np.uint8) * 255
    # Connect strokes belonging to one candidate without prescribing row/column
    # counts. The kernel scales with resolution, not with an assumed reference grid.
    k = max(3, int(round(min(w, h) * 0.012)))
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2*k+1, 2*k+1))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    mask = cv2.dilate(mask, kernel, iterations=1)
    count, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    min_area = max(20, int(w * h * min_component_area_fraction))
    boxes = []
    for idx in range(1, count):
        x, y, bw, bh, area = stats[idx]
        if area < min_area or bw < max(4, w // 100) or bh < max(4, h // 100):
            continue
        pad = max(2, int(round(min(bw, bh) * 0.06)))
        x0, y0 = max(0, x-pad), max(0, y-pad)
        x1, y1 = min(w, x+bw+pad), min(h, y+bh+pad)
        boxes.append({"x": int(x0), "y": int(y0), "width": int(x1-x0), "height": int(y1-y0), "area": int(area)})
    boxes.sort(key=lambda b: (b["y"], b["x"]))
    return {
        "image_width_px": w, "image_height_px": h,
        "estimated_background_rgb": tuple(int(round(v)) for v in bg),
        "candidate_count": len(boxes),
        "candidate_boxes_px": boxes,
        "status": "segmentation_candidates_require_visual_review",
        "nonclaim": "Candidate boxes are not automatically promoted to digitized eyes.",
    }


def write_acquisition_manifest(records: list[ReferenceAcquisitionRecord], path: str | Path) -> None:
    payload = {"schema_version": "V1.9-acquisition-1", "records": [asdict(r) for r in records]}
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
