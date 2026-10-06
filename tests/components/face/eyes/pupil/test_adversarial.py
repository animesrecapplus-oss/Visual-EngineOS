import math  # ADV-PUPIL-001: generate non-finite hostile values.
import pytest  # ADV-PUPIL-001: assert explicit rejection.
from visual_engine.components.face.eyes.pupil.effects import PupilGlowSpec, PupilSmokeSpec  # ADV-PUPIL-005: effect boundary attacks.
from visual_engine.components.face.eyes.pupil.spec import PupilSpec  # ADV-PUPIL-001: pupil boundary attacks.

@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])  # ADV-PUPIL-001: attack all non-finite classes.
def test_pupil_rejects_non_finite(value):  # ADV-PUPIL-001: non-finite local state is forbidden.
    with pytest.raises(ValueError):  # ADV-PUPIL-001: construction must fail explicitly.
        PupilSpec(x=value)  # ADV-PUPIL-001: inject the hostile value.

@pytest.mark.parametrize("field", ["scale", "scale_x", "scale_y"])  # ADV-PUPIL-002: attack every positive scale channel.
def test_pupil_rejects_non_positive_scales(field):  # ADV-PUPIL-002: zero and negative scale are impossible states.
    with pytest.raises(ValueError):  # ADV-PUPIL-002: invalid scale must fail.
        PupilSpec(**{field: 0.0})  # ADV-PUPIL-002: inject the boundary value.

@pytest.mark.parametrize("opacity", [-0.001, 1.001])  # ADV-PUPIL-003: attack both opacity bounds.
def test_pupil_rejects_invalid_opacity(opacity):  # ADV-PUPIL-003: opacity must remain bounded.
    with pytest.raises(ValueError):  # ADV-PUPIL-003: invalid opacity must fail.
        PupilSpec(opacity=opacity)  # ADV-PUPIL-003: inject the invalid value.

def test_effect_specs_reject_invalid_bounds():  # ADV-PUPIL-005: effect limits must fail explicitly.
    with pytest.raises(ValueError):  # ADV-PUPIL-005: glow intensity cannot exceed one.
        PupilGlowSpec(intensity=1.001)  # ADV-PUPIL-005: inject invalid intensity.
    with pytest.raises(ValueError):  # ADV-PUPIL-005: smoke opacity cannot be negative.
        PupilSmokeSpec(opacity=-0.001)  # ADV-PUPIL-005: inject invalid opacity.
    with pytest.raises(ValueError):  # ADV-PUPIL-007: smoke requires at least one wisp.
        PupilSmokeSpec(wisps=0)  # ADV-PUPIL-007: inject invalid count.
