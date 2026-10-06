from __future__ import annotations

from pathlib import Path
import json

from .digitization import ReferenceDigitizationSet, ReferenceFamily, ReferenceSample, ReferenceSource


def load_v18_reference_envelope_dataset() -> ReferenceDigitizationSet:
    """Load the measured V1.4 envelope evidence without pretending it is pixel digitization."""
    path = Path(__file__).with_name("REFERENCE_DIGITIZATION_STATUS.json")
    payload = json.loads(path.read_text(encoding="utf-8"))
    source = ReferenceSource(**payload["source"])
    samples = tuple(
        ReferenceSample(
            sample_id=row["sample_id"],
            family=ReferenceFamily(row["family"]),
            envelope_width_px=row["envelope_width_px"],
            envelope_height_px=row["envelope_height_px"],
            notes=row.get("notes", ""),
        )
        for row in payload["measured_envelopes"]
    )
    return ReferenceDigitizationSet(
        schema_version=payload["schema_version"], source=source, samples=samples,
        provenance=payload["provenance"], status=payload["status"],
    )
