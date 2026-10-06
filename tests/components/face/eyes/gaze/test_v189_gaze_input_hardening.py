import math

import pytest

from visual_engine.components.face.eyes.gaze.solver import Gaze


@pytest.mark.parametrize("field", ["x", "y", "strength", "amplitude"])
def test_TST_GAZE_001_numeric_fields_reject_bool(field):
    with pytest.raises((TypeError, ValueError)):
        Gaze(**{field: True})


@pytest.mark.parametrize("field", ["x", "y", "strength", "amplitude"])
def test_ADV_GAZE_001_numeric_fields_reject_numeric_strings(field):
    with pytest.raises((TypeError, ValueError)):
        Gaze(**{field: "0.5"})


@pytest.mark.parametrize("field", ["x", "y", "strength", "amplitude"])
@pytest.mark.parametrize("value", [math.nan, math.inf, -math.inf])
def test_ADV_GAZE_002_numeric_fields_reject_non_finite(field, value):
    with pytest.raises(ValueError):
        Gaze(**{field: value})


def test_ADV_GAZE_003_huge_numeric_input_fails_closed():
    with pytest.raises(ValueError):
        Gaze(x=10**10000)


@pytest.mark.parametrize("target", [(True, 0.0), (0.0, True), ("0.0", 0.0), (0.0, "0.0")])
def test_ADV_GAZE_004_target_rejects_non_real_elements(target):
    with pytest.raises(ValueError):
        Gaze(target=target)


@pytest.mark.parametrize("target", [(math.nan, 0.0), (0.0, math.inf), (0.0, -math.inf)])
def test_ADV_GAZE_005_target_rejects_non_finite_elements(target):
    with pytest.raises(ValueError):
        Gaze(target=target)


def test_ADV_GAZE_006_huge_target_fails_closed():
    with pytest.raises(ValueError):
        Gaze(target=(10**10000, 0.0))


def test_ADV_GAZE_007_target_requires_immutable_tuple():
    with pytest.raises(ValueError):
        Gaze(target=[0.0, 0.0])


@pytest.mark.parametrize("target", [(), (0.0,), (0.0, 0.0, 0.0), "00"])
def test_ADV_GAZE_008_target_requires_exact_pair_shape(target):
    with pytest.raises(ValueError):
        Gaze(target=target)


@pytest.mark.parametrize("direction", [None, True, 1, "diagonal", "RIGHT"])
def test_ADV_GAZE_009_direction_runtime_vocabulary_is_closed(direction):
    with pytest.raises(ValueError):
        Gaze(direction=direction)


def test_TST_GAZE_002_valid_authored_values_are_preserved_without_coercion():
    gaze = Gaze(x=0.25, y=-0.125, strength=0.75, direction="upper_right", target=(2.0, -1.0), amplitude=0.5)
    assert gaze.x == 0.25
    assert gaze.y == -0.125
    assert gaze.strength == 0.75
    assert gaze.direction == "upper_right"
    assert gaze.target == (2.0, -1.0)
    assert gaze.amplitude == 0.5


def test_TST_GAZE_003_zero_strength_and_amplitude_remain_valid():
    assert Gaze(strength=0.0).strength == 0.0
    assert Gaze(amplitude=0.0).amplitude == 0.0


@pytest.mark.parametrize("field", ["strength", "amplitude"])
def test_ADV_GAZE_010_negative_magnitude_is_rejected(field):
    with pytest.raises(ValueError):
        Gaze(**{field: -1.0})


def test_TST_GAZE_004_vector_semantics_remain_unchanged_for_named_direction():
    gaze = Gaze(direction="upper_right", x=0.1, y=-0.2)
    assert gaze.vector() == pytest.approx((0.80710678, -0.90710678))


def test_TST_GAZE_005_vector_semantics_remain_unchanged_for_target():
    gaze = Gaze(target=(20.0, 10.0), x=0.25, y=-0.5)
    assert gaze.vector(center=(10.0, 20.0)) == pytest.approx((10.25, -10.5))


def test_TST_GAZE_006_gaze_remains_immutable():
    gaze = Gaze(target=(1.0, 2.0))
    with pytest.raises((AttributeError, TypeError)):
        gaze.x = 2.0
