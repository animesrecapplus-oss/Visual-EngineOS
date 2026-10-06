import math

import pytest

from visual_engine.components.face.eyes.iris.spec import IrisSpec


@pytest.mark.parametrize("field", ["glow", "opacity", "pattern_strength", "outline_width"])
@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_iris_rejects_non_finite_real_fields(field: str, value: float) -> None:
    with pytest.raises(ValueError):
        IrisSpec(**{field: value})


@pytest.mark.parametrize("field", ["glow", "opacity", "pattern_strength", "outline_width"])
def test_iris_rejects_bool_as_real_state(field: str) -> None:
    with pytest.raises(ValueError):
        IrisSpec(**{field: True})


@pytest.mark.parametrize("field", ["ring_count", "pattern_count"])
def test_iris_rejects_bool_and_fractional_counts(field: str) -> None:
    with pytest.raises(ValueError):
        IrisSpec(**{field: True})
    with pytest.raises(ValueError):
        IrisSpec(**{field: 2.5})


def test_iris_rejects_coercive_string_numeric_state() -> None:
    with pytest.raises(ValueError):
        IrisSpec(glow="0.5")


def test_iris_rejects_non_finite_outline_width_without_changing_valid_values() -> None:
    with pytest.raises(ValueError):
        IrisSpec(outline_width=math.nan)
    iris = IrisSpec(ring_count=2, pattern_count=16, glow=0.18, opacity=0.98, pattern_strength=0.38, outline_width=0.018)
    assert (iris.ring_count, iris.pattern_count, iris.glow, iris.opacity, iris.pattern_strength, iris.outline_width) == (2, 16, 0.18, 0.98, 0.38, 0.018)
