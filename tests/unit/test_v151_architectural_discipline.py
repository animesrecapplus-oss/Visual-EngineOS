from __future__ import annotations  # V1.51: keep governance tests portable.

from pathlib import Path  # V1.51: resolve the repository root.

from tools.audit_v151_source_modularization import run  # V1.51: exercise the source audit as a real test.
from tools.validate_v151_domain_resolution_truth import validate  # V1.51: exercise the component truth gate.


def _root() -> Path:  # V1.51: derive the repository root from the test location.
    return Path(__file__).resolve().parents[2]  # V1.51: tests/unit is two levels below the repository root.


def test_domain_resolution_component_truth_gate_passes() -> None:  # V1.51: dossier completeness is a release condition.
    report = validate()  # V1.51: execute the read-only component gate.
    assert report["ok"], report  # V1.51: no hidden governance defect may pass.


def test_selected_owner_has_no_cycle_or_duplicate() -> None:  # V1.51: architectural ownership must be unique and acyclic.
    report = run()  # V1.51: rebuild the dependency and duplicate evidence.
    assert report["selected_new_owner"] == "visual_engine.runtime.domain_result_validation"  # V1.51: owner identity is explicit.
    assert not any("domain_result_validation" in member for cycle in report["strongly_connected_cycles"] for member in cycle)  # V1.51: the new owner must not create a cycle.
    assert report["exact_duplicate_function_groups"] == []  # V1.51: no exact duplicate implementation is accepted.


def test_persistence_boundary_is_unchanged() -> None:  # V1.51: database impact must remain explicitly absent.
    report = run()  # V1.51: execute the same persistence boundary audit used for certification.
    assert report["persistence_direct_consumer"] is False  # V1.51: no persistence module may own this responsibility.


def test_all_durable_documents_remain_bounded() -> None:  # V1.51: documentation debt must not grow silently.
    root = _root()  # V1.51: resolve the repository root.
    oversized = [str(path) for path in (root / "docs").rglob("*.md") if len(path.read_text(encoding="utf-8").splitlines()) > 150]  # V1.51: scan every durable Markdown file.
    assert oversized == []  # V1.51: certification requires bounded documentation.
