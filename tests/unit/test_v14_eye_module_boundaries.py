"""Architectural regression tests for the V1.4 eye module decomposition."""
from pathlib import Path


EYES = Path(__file__).parents[2] / "src" / "visual_engine" / "components" / "face" / "eyes"


def test_eye_implementation_files_stay_below_fourre_tout_budget():
    """Focused implementation files must remain small enough to audit precisely."""
    excluded = {"core.py", "definitions.py", "geometry_builder.py"}
    offenders = []
    for path in EYES.rglob("*.py"):
        if path.name in excluded:
            continue
        lines = len(path.read_text(encoding="utf-8").splitlines())
        if lines > 250:
            offenders.append((str(path.relative_to(EYES)), lines))
    assert offenders == []


def test_historical_facades_contain_no_domain_class_definitions():
    """Compatibility facades must not become new implementation containers."""
    for name in ("core.py", "definitions.py", "geometry_builder.py"):
        text = (EYES / name).read_text(encoding="utf-8")
        assert "class " not in text
        assert "def build_eye_geometry" not in text


def test_domain_ownership_directories_exist():
    required = {
        "contracts", "morphology", "pupil", "iris", "eyelid", "lashes",
        "eyebrow", "highlights", "gaze", "geometry", "appearance",
    }
    assert {p.name for p in EYES.iterdir() if p.is_dir()} >= required
