import pytest
from visual_engine.scene.shot import Shot, ShotScale


def test_shot_scales_are_explicit_and_renderer_agnostic():
    assert Shot(ShotScale.CLOSE_UP).scale is ShotScale.CLOSE_UP
    assert Shot(ShotScale.DISTANT).scale is ShotScale.DISTANT


def test_shot_fill_ratio_is_bounded():
    with pytest.raises(ValueError):
        Shot(fill_ratio=0)
    with pytest.raises(ValueError):
        Shot(fill_ratio=1.1)
