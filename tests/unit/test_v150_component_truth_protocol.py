import json  # TEST: inspect the machine-readable component manifest.
from pathlib import Path  # TEST: resolve the repository files.
from tools.validate_component_truth import validate  # TEST: exercise the same gate used by CI/manual review.


def test_pupil_component_truth_gate_passes():  # TEST: the pilot dossier must satisfy every mandatory structural gate.
    root = Path(__file__).resolve().parents[2]  # TEST: resolve repository root from tests/unit.
    report = validate(root, root / "docs/components/eyes/pupil")  # TEST: run the read-only protocol gate.
    assert report["ok"], report  # TEST: no hidden governance defect is accepted.


def test_pupil_manifest_has_stable_identity():  # TEST: component identity must not drift.
    root = Path(__file__).resolve().parents[2]  # TEST: resolve repository root.
    data = json.loads((root / "docs/components/eyes/pupil/MANIFEST.json").read_text(encoding="utf-8"))  # TEST: load the manifest.
    assert data["component_id"] == "CMP-EYE-PUPIL"  # TEST: stable ID is mandatory.
    assert data["semantic_path"] == "face/eyes/pupil"  # TEST: semantic ownership is mandatory.
