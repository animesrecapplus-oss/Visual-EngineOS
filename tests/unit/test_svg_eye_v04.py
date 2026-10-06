from visual_engine.geometry import EyeParameters, build_eye_geometry
from visual_engine.render import eye_outer_path, render_eye_svg


def test_eye_svg_is_vector_and_contains_expected_surfaces():
    svg = render_eye_svg(build_eye_geometry(EyeParameters()))
    assert svg.startswith("<svg ")
    assert "<path" in svg
    assert "<ellipse" in svg
    assert "<circle" in svg
    assert "clipPath" in svg
    assert "<image" not in svg


def test_outer_path_is_deterministic():
    g = build_eye_geometry(EyeParameters(asymmetry=0.2))
    assert eye_outer_path(g) == eye_outer_path(g)
