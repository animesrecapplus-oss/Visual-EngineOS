from __future__ import annotations

from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
SRC = ROOT / "src"
TOOL = ROOT / "tools" / "verify_v133_color_downstream_closure.py"


def _run_gate() -> str:
    result = subprocess.run(
        [sys.executable, str(TOOL)],
        cwd=ROOT,
        env={**__import__("os").environ, "PYTHONPATH": str(SRC)},
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def _report() -> dict:
    from tools.audit_v133_color_downstream_closure import audit
    return audit()


def test_no_production_downstream_caller_is_proven() -> None:
    output = _run_gate()
    report = _report()
    assert "V1.33_COLOR_DOWNSTREAM_CLOSURE_GATE: PASS" in output
    assert report["production_downstream_edges"] == []
    assert report["migration_allowed"] is False


def test_only_resolver_incoming_edge_is_internal_wrapper() -> None:
    report = _report()
    incoming = report["resolver_incoming_edges"]
    assert len(incoming) == 1
    edge = incoming[0]
    assert edge["path"] == "src/visual_engine/runtime/color_resolution.py"
    assert edge["caller"].endswith("resolve_color_domain_from_typed")
    assert edge["callee"].endswith("resolve_color_domain")


def test_dynamic_escape_hatches_are_empty() -> None:
    report = _report()
    assert report["dynamic_escape_hatch_findings"] == []


def test_v133_historical_audit_remains_compatible_with_the_current_runtime_policy() -> None:
    policy = (SRC / "visual_engine" / "runtime" / "version_policy.py").read_text(encoding="utf-8")
    project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    assert 'ENGINE_VERSION = "1.3.8"' in policy
    assert 'RESOLUTION_VERSION = "20"' in policy
    assert 'version = "1.3.8"' in project
