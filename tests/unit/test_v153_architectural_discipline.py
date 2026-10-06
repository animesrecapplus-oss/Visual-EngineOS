from __future__ import annotations

import ast
from pathlib import Path

from tools.audit_v153_domain_input_contract import run
from tools.validate_v153_domain_input_truth import validate


def test_v153_component_gate_passes():
    report = validate()
    assert report["ok"], report


def test_v153_owner_is_acyclic_and_unique():
    report = run()
    assert report["selected_new_owner"] == "visual_engine.runtime.domain_input_contract"
    assert not any("domain_input_contract" in member for cycle in report["strongly_connected_cycles"] for member in cycle)
    assert report["exact_duplicate_function_groups"] == []


def test_v153_owner_does_not_import_legacy_facade():
    root = Path(__file__).resolve().parents[2]
    owner = root / "src/visual_engine/runtime/domain_input_contract.py"
    tree = ast.parse(owner.read_text(encoding="utf-8"))
    assert not any(
        isinstance(node, ast.ImportFrom) and node.module == "visual_engine.runtime.domain_resolution"
        for node in ast.walk(tree)
    )


def test_v153_persistence_boundary_is_absent():
    assert run()["persistence_direct_consumer"] is False
