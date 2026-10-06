from __future__ import annotations

from pathlib import Path
from tools.document_loader import read_document_any

ROOT = Path(__file__).parents[2]
SCRIPT = ROOT / "tools" / "scripts_visual_qa_v13_feedback.py"
VERIFIER = ROOT / "tools" / "verify_a5_visual_qa.py"
RETENTION_DOC = None
V17_CONTRACT = None


def test_a5_reproduction_sources_remain_archived_as_source_code():
    """Historical A5 remains reproducible from source even though old output files are not retained."""
    assert SCRIPT.is_file()
    assert VERIFIER.is_file()
    text = read_document_any("ARTIFACT_RETENTION_POLICY.md")
    assert "artifacts/` is part of the project" in text
    assert "Older generated evidence is purged" in text


def test_current_artifact_policy_is_documented_outside_legacy_a5_outputs():
    """Artifact retention is validated by the V1.7 verifier after QA generation, not by a stale V1.3 fixture."""
    text = read_document_any("ARTIFACT_RETENTION_POLICY.md")
    assert "Retained" in text
    assert "Purged before certification" in text
