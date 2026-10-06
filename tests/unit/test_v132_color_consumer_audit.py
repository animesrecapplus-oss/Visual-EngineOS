from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
AUDIT = ROOT / "tools" / "audit_v132_color_consumers.py"


def _run_audit() -> dict:
    from tools.audit_v132_color_consumers import audit
    return audit()


def test_audit_finds_no_downstream_color_consumer_in_current_production_tree() -> None:
    report = _run_audit()
    assert report["production_python_files"] >= 100
    assert report["production_downstream_color_consumers"] == 0
    assert report["migration_status"] == "NONE_WARRANTED"
    assert report["resolver_production_calls"] == []


def test_audit_classifies_every_finding_and_preserves_requested_categories() -> None:
    report = _run_audit()
    assert report["unclassified_findings"] == []
    counts = report["category_counts"]
    for category in (
        "canonical_color",
        "color_operation",
        "effect",
        "legacy_compatibility",
        "palette",
        "supporting_infrastructure",
    ):
        assert counts.get(category, 0) > 0


def test_audit_does_not_claim_dead_code_without_reachability_evidence() -> None:
    report = _run_audit()
    assert report["dead_code_candidates"] == []
    assert report["criteria"]["dead_code"].startswith("not assigned")
