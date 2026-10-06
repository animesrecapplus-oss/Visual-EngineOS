from visual_engine.geometry import *
from visual_engine.render import render_eye_svg


def test_svg_contains_vector_layers():
    a=EyeAppearance(
        pupils=(PupilSpec(shape="diamond", color="#ff00aa"), PupilSpec(x=.2, color="#00ffaa")),
        iris=IrisSpec(ring_count=2, glow=.5),
        lashes=LashSpec(enabled=True, count=4),
        eyebrow=BrowSpec(enabled=True, shape="high_arch"),
    )
    svg=render_eye_svg(build_eye_geometry(EyeParameters(shape="round", contour_irregularity=.7, contour_wave_amplitude=.3), appearance=a), appearance=a)
    assert "<svg" in svg and "<path" in svg and "<ellipse" in svg and "<polygon" in svg and "<line" in svg
    assert "high_arch" not in svg  # semantic name is resolved into geometry, not leaked to SVG


def test_closed_eye_has_no_pupil_or_iris_primitives():
    svg=render_eye_svg(build_eye_geometry(EyeParameters(), state="closed"))
    assert "<ellipse" not in svg


def test_svg_supports_complex_iris_and_stable_clip_id():
    from visual_engine.geometry import EyeAppearance, IrisSpec, PupilSpec
    from visual_engine.render import render_eye_svg
    a = EyeAppearance(iris=IrisSpec(shape="hexagon", pattern="radial", pattern_strength=.5))
    g = build_eye_geometry(appearance=a)
    svg1 = render_eye_svg(g, appearance=a)
    svg2 = render_eye_svg(g, appearance=a)
    assert "<polygon" in svg1 and "<line" in svg1
    assert svg1 == svg2


def test_state_has_visible_semantic_effects():
    from visual_engine.render import render_eye_svg
    crying = render_eye_svg(build_eye_geometry(state="crying"))
    irritated = render_eye_svg(build_eye_geometry(state="irritated"))
    damaged = render_eye_svg(build_eye_geometry(state="damaged"))
    assert "#8fd8ff" in crying
    assert "#d44" in irritated
    assert "#8b1e1e" in damaged
