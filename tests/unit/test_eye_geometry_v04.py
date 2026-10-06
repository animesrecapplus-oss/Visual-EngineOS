import pytest

from visual_engine.geometry import EyeParameters, build_eye_geometry


def test_default_eye_is_deterministic_and_non_degenerate():
    a = build_eye_geometry(EyeParameters(), center=(10, 20))
    b = build_eye_geometry(EyeParameters(), center=(10, 20))
    assert a == b
    assert a.nominal_width > 0
    assert a.visible_height > 0


def test_opening_controls_visible_height():
    full = build_eye_geometry(EyeParameters(opening=1.0))
    half = build_eye_geometry(EyeParameters(opening=0.5))
    assert half.visible_height < full.visible_height
    assert half.visible_height > 0


def test_closed_eye_has_no_visible_iris_aperture():
    closed = build_eye_geometry(EyeParameters(opening=1.0), state="closed")
    assert closed.opening == 0
    assert closed.visible_height == 0


def test_ratios_propagate_from_eye_to_iris_and_pupil():
    p = EyeParameters(height=0.8, iris_ratio=0.5, pupil_ratio=0.4)
    g = build_eye_geometry(p)
    assert g.iris_rx == pytest.approx(0.2)
    assert g.pupil_rx == pytest.approx(0.08)


def test_invalid_parameters_are_rejected():
    with pytest.raises(ValueError):
        EyeParameters(width=0)
    with pytest.raises(ValueError):
        EyeParameters(opening=1.1)
    with pytest.raises(ValueError):
        EyeParameters(iris_ratio=0)
