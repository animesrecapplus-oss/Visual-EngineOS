import re

from visual_engine.geometry import (
    BrowSpec,
    EyeAppearance,
    EyeParameters,
    Gaze,
    LashSpec,
    LowerLashSpec,
    PupilSmokeSpec,
    PupilSpec,
    build_eye_geometry,
)
from visual_engine.render import render_eye_svg


def test_round_shape_is_circular_at_full_opening():
    g = build_eye_geometry(EyeParameters(shape="round", width=2.0, height=0.55))
    xs = [x for x, _ in g.contour_points]
    ys = [y for _, y in g.contour_points]
    ratio = (max(xs) - min(xs)) / (max(ys) - min(ys))
    assert abs(ratio - 1.0) < 0.01


def test_ellipse_shape_remains_the_explicit_non_circular_option():
    g = build_eye_geometry(EyeParameters(shape="ellipse", width=2.0, height=0.55))
    xs = [x for x, _ in g.contour_points]
    ys = [y for _, y in g.contour_points]
    assert (max(xs) - min(xs)) > (max(ys) - min(ys)) * 1.5


def test_gaze_moves_iris_pupil_and_highlight_as_one_assembly():
    app = EyeAppearance()
    center = build_eye_geometry(EyeParameters(width=2, height=1), gaze=Gaze(direction="center"), appearance=app)
    right = build_eye_geometry(EyeParameters(width=2, height=1), gaze=Gaze(direction="right"), appearance=app)
    assert right.iris_center[0] > center.iris_center[0]
    assert right.pupil_center == right.iris_center
    assert right.reflection_center[0] > center.reflection_center[0]


def test_custom_multi_pupil_offset_is_still_clamped_to_the_iris():
    app = EyeAppearance(pupils=(PupilSpec(x=100, y=-100, scale=1.5),))
    g = build_eye_geometry(EyeParameters(width=2, height=1), appearance=app)
    px, py = g.pupil_center
    ix, iy = g.iris_center
    q = ((px - ix) / g.iris_rx) ** 2 + ((py - iy) / g.iris_ry) ** 2
    assert q <= 1.000001


def test_default_upper_lashes_are_shorter_and_heavier_than_lower_lashes():
    a = EyeAppearance()
    assert a.lashes.length < 0.10
    assert a.lashes.thickness > a.lower_lashes.thickness
    assert a.lower_lashes.density < a.lashes.density


def test_brow_variants_produce_distinct_geometry():
    g = build_eye_geometry()
    svgs = {
        name: render_eye_svg(g, appearance=EyeAppearance(eyebrow=BrowSpec(shape=name, density=1.0)))
        for name in ("short", "long", "thick", "dense", "arched", "ornate", "faded")
    }
    assert len(set(svgs.values())) == len(svgs)
    assert 'opacity="0.420000"' in svgs["faded"]
    assert svgs["ornate"].count("<circle") >= 3


def test_inward_brow_uses_bilateral_side_when_rendering_a_pair():
    from visual_engine.geometry import build_eye_pair, EyePairSpec
    from visual_engine.render import render_eye_pair_svg
    pair = build_eye_pair(EyePairSpec(base_appearance=EyeAppearance(eyebrow=BrowSpec(shape="inward"))))
    svg = render_eye_pair_svg(pair)
    assert svg.count('stroke="#000000"') >= 2


def test_gaze_follow_changes_lid_geometry():
    center = build_eye_geometry(EyeParameters(width=2, height=1), gaze=Gaze(direction="center"))
    down = build_eye_geometry(EyeParameters(width=2, height=1), gaze=Gaze(direction="down"))
    assert center.upper_lid_points != down.upper_lid_points
    assert center.lower_lid_points != down.lower_lid_points


def test_smoke_is_emitted_as_visible_escaping_paths():
    smoke = PupilSmokeSpec(enabled=True, color="#8a8f99", opacity=.65, length=.8, width=.10, curl=.25, wisps=3)
    app = EyeAppearance(pupils=(PupilSpec(smoke=smoke),))
    svg = render_eye_svg(build_eye_geometry(EyeParameters(shape="round"), appearance=app), appearance=app, background="#ffffff")
    paths = re.findall(r'<path d="M [^"]+"[^>]*stroke="#8a8f99"', svg)
    assert len(paths) == 6
    assert 'stroke-linecap="round"' in svg
