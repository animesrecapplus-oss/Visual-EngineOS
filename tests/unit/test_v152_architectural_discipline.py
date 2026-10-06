from __future__ import annotations

from pathlib import Path

from tools.audit_v152_domain_result_contract import run
from tools.validate_v152_domain_resolution_truth import validate


def test_v152_component_gate_passes():
    report = validate()
    assert report["ok"], report


def test_v152_owner_is_acyclic_and_unique():
    report = run()
    assert report["selected_new_owner"] == "visual_engine.runtime.domain_result_contract"
    assert not any("domain_result_contract" in member for cycle in report["strongly_connected_cycles"] for member in cycle)
    assert report["exact_duplicate_function_groups"] == []


def test_v152_persistence_boundary_is_absent():
    assert run()["persistence_direct_consumer"] is False


def test_v152_durable_docs_are_bounded():
    root = Path(__file__).resolve().parents[2]
    oversized = [str(path) for path in (root / "docs").rglob("*.md") if len(path.read_text(encoding="utf-8").splitlines()) > 150]
    assert oversized == []
