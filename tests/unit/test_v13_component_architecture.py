from pathlib import Path


def test_component_ownership_tree_exists():
    root = Path("src/visual_engine/components")
    for rel in (
        "common/meta.py",
        "common/visual_contract.py",
        "common/geometry_contract.py",
        "face/eyes/core.py",
        "face/eyes/pair.py",
        "face/eyes/pupil/__init__.py",
        "face/eyes/iris/__init__.py",
        "face/eyes/eyelid/__init__.py",
        "face/eyes/lashes/__init__.py",
        "face/eyes/eyebrow/__init__.py",
        "face/eyes/highlights/__init__.py",
        "face/eyes/effects/__init__.py",
    ):
        assert (root / rel).is_file(), rel


def test_legacy_eye_import_is_the_same_implementation_owner():
    from visual_engine.geometry.eye import EyeParameters as LegacyEyeParameters
    from visual_engine.components.face.eyes.core import EyeParameters
    assert LegacyEyeParameters is EyeParameters


def test_legacy_common_import_is_the_same_implementation_owner():
    from visual_engine.model.visual_contract import VisualContract as LegacyVisualContract
    from visual_engine.components.common.visual_contract import VisualContract
    assert LegacyVisualContract is VisualContract
