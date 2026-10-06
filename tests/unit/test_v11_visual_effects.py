from dataclasses import replace
import re

from visual_engine.geometry import (
    EyeAppearance, EyeParameters, LashSpec, LashShadowSpec, PupilGlowSpec,
    PupilSmokeSpec, PupilSpec, build_eye_geometry,
)
from visual_engine.render import render_eye_svg


def _shadow_opacity(svg: str) -> float:
    m = re.search(r'filter="url\(#lash-shadow-filter-[^"]+\)"[^>]*/>', svg)
    assert m
    before = svg[max(0, m.start()-120):m.end()]
    om = re.search(r'opacity="([0-9.]+)"', before)
    assert om
    return float(om.group(1))


def test_upper_lash_shadow_is_continuous_and_inside_aperture():
    svg = render_eye_svg(build_eye_geometry(), appearance=EyeAppearance())
    assert "lash-shadow-filter-" in svg
    assert 'clip-path="url(#eye-clip-' in svg
    assert "feGaussianBlur" in svg


def test_denser_thicker_longer_upper_lashes_cast_a_stronger_shadow():
    g = build_eye_geometry()
    base = EyeAppearance(lashes=LashSpec(density=.2, thickness=.008, length=.05, count=8))
    heavy = EyeAppearance(lashes=LashSpec(density=1.0, thickness=.035, length=.20, count=30))
    assert _shadow_opacity(render_eye_svg(g, appearance=heavy)) > _shadow_opacity(render_eye_svg(g, appearance=base))


def test_lash_forms_render_as_distinct_geometry():
    g = build_eye_geometry()
    outputs = {}
    for form in ("line", "tapered", "clustered", "disheveled"):
        a = EyeAppearance(lashes=LashSpec(form=form, density=1, count=10))
        outputs[form] = render_eye_svg(g, appearance=a)
    assert len(set(outputs.values())) == 4
    assert "<polygon" not in outputs["line"]
    assert "fill=\"#000000\"" in outputs["tapered"]


def test_pupil_can_glow_without_changing_pupil_identity():
    spec = PupilSpec(color="#ff2200", glow=PupilGlowSpec(enabled=True, intensity=1.0, core_intensity=1.0))
    svg = render_eye_svg(build_eye_geometry(), appearance=EyeAppearance(pupils=(spec,)))
    assert "pupil-glow-" in svg
    assert 'fill="#ff2200"' in svg
    assert "feGaussianBlur" in svg


def test_pupil_smoke_defaults_upward():
    spec = PupilSpec(smoke=PupilSmokeSpec(enabled=True, opacity=.6, wisps=3))
    svg = render_eye_svg(build_eye_geometry(), appearance=EyeAppearance(pupils=(spec,)))
    # Default direction is -90 degrees in SVG coordinates: upward.
    assert 'stroke="#ffffff"' in svg
    paths = re.findall(r'<path d="M ([^,]+),([^ ]+) C ([^,]+),([^ ]+) ([^,]+),([^ ]+) ([^,]+),([^ ]+)"[^>]*stroke="#ffffff"[^>]*/>', svg)
    assert paths
    first = paths[0]
    sy = float(first[1]); ey = float(first[7])
    assert ey < sy


def test_pupil_effects_are_off_by_default():
    svg = render_eye_svg(build_eye_geometry(), appearance=EyeAppearance())
    assert "pupil-glow-" not in svg
    # No smoke stroke is emitted by the pupil effect layer.
    assert 'stroke="#ffffff"' not in svg
