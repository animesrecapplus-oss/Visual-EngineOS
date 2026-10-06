from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[5]


def test_pupil_semantic_parent_is_iris_and_aggregate_parent_is_eye():
    data = json.loads(
        (ROOT / "docs/governance/architecture/EYE_SEMANTIC_HIERARCHY_MATRIX__V1.83.json").read_text()
    )
    pupil = data["pupil"]
    assert pupil["semantic_parent"] == "CMP-EYE-IRIS"
    assert pupil["aggregate_parent"] == "CMP-EYE"
    assert pupil["runtime_changed"] is False


def test_pupil_dossier_contains_corrected_relation():
    base = ROOT / "docs/components/eyes/pupil"
    text = "\n".join((base / name).read_text() for name in ("INDEX.md", "COMPONENT_TRUTH.md", "RELATIONS.md"))
    assert "CMP-EYE-IRIS" in text
    assert "V1.15/V1.17" in text


def test_eye_matrix_rejects_linear_periocular_parent_chain():
    text = (ROOT / "docs/governance/architecture/EYE_SEMANTIC_HIERARCHY_MATRIX__V1.83.md").read_text()
    assert "is **false**" in text
    assert "IRIS → PUPIL` is **true**" in text
