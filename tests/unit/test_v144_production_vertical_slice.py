from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def test_current_artifact_area_contains_only_the_latest_brick():
    # Generated evidence is current-only: the artifacts directory remains, while
    # superseded history/release trees must not accumulate across checkpoints.
    artifacts = ROOT / "artifacts"
    current = artifacts / "current"
    assert artifacts.is_dir()
    assert current.is_dir()
    assert not (artifacts / "history").exists()
    assert not (artifacts / "releases").exists()
    versions = [path for path in current.iterdir() if path.is_dir()]
    assert len(versions) <= 1
    reports = sorted((ROOT / "docs" / "runtime" / "production").glob("V1.44_IMPLEMENTATION_REPORT_2026-09-29__part_*.md"))
    assert reports
    text = "\n".join(p.read_text(encoding="utf-8") for p in reports)
    assert "AUDIT-ONLY / NO PRODUCTION VERTICAL-SLICE CALLER" in text
    assert "V1.44_PRODUCTION_VERTICAL_SLICE_GATE: PASS" in text


def test_v144_historical_boundary_is_not_used_as_a_current_production_claim():
    report = "\n".join(p.read_text(encoding="utf-8") for p in sorted((ROOT / "docs" / "runtime" / "production").glob("V1.44_IMPLEMENTATION_REPORT_2026-09-29__part_*.md")))
    assert "no production-owned request that connects them into one" in report
    assert "runtime path" in report
    from visual_engine.runtime.production_render_session import ProductionRenderSession
    from visual_engine.runtime.production_slice import ProductionRenderSession as CompatibilitySession
    assert CompatibilitySession is ProductionRenderSession


def test_v144_historical_report_remains_the_provenance_record():
    report = "\n".join(p.read_text(encoding="utf-8") for p in sorted((ROOT / "docs" / "runtime" / "production").glob("V1.44_IMPLEMENTATION_REPORT_2026-09-29__part_*.md")))
    assert "changed production source files: 0" in report
    assert "A8" in report
