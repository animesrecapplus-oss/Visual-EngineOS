from __future__ import annotations

import math

import pytest

from visual_engine.components.face.eyes.pupil.spec import PupilSpec


@pytest.mark.parametrize("field", ["x", "y", "scale", "scale_x", "scale_y", "rotation_deg", "outline_width", "opacity"])
def test_pupil_rejects_boolean_numeric_state(field: str) -> None:
    with pytest.raises(ValueError, match="finite numeric"):
        PupilSpec(**{field: True})


@pytest.mark.parametrize("field", ["x", "y", "rotation_deg"])
def test_pupil_rejects_coercive_non_numeric_state(field: str) -> None:
    with pytest.raises(ValueError, match="finite numeric"):
        PupilSpec(**{field: "0.5"})


@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_pupil_rejects_non_finite_outline_width(value: float) -> None:
    with pytest.raises(ValueError, match="finite numeric"):
        PupilSpec(outline_width=value)


def test_valid_outline_width_remains_accepted() -> None:
    pupil = PupilSpec(outline_width=0.008)
    assert pupil.outline_width == 0.008
