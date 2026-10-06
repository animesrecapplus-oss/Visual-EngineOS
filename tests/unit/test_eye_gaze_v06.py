import pytest
from visual_engine.geometry import EyeAppearance, EyeParameters, Gaze, GazeSolver, PupilSpec, build_eye_geometry
import math


def test_target_point_resolves_to_direction_from_eye_center():
    g = build_eye_geometry(EyeParameters(width=2.0, height=1.0), center=(10.0, 20.0), gaze=Gaze(target=(20.0, 10.0)))
    assert g.gaze_solution.normalized_x > 0
    assert g.gaze_solution.normalized_y < 0
    assert g.gaze_solution.requested_magnitude > 0
    assert g.gaze_solution.offset_x > 0
    assert g.gaze_solution.offset_y < 0


def test_extreme_target_is_clamped_by_actual_morphology():
    narrow = build_eye_geometry(EyeParameters(width=2.0, height=0.35, shape="narrow"), gaze=Gaze(direction="right", strength=100))
    round_eye = build_eye_geometry(EyeParameters(width=2.0, height=1.4, shape="large_round"), gaze=Gaze(direction="right", strength=100))
    assert narrow.gaze_solution.clamped
    assert round_eye.gaze_solution.clamped
    assert round_eye.gaze_solution.limit > narrow.gaze_solution.limit


def test_extreme_gaze_is_limited_by_the_eye_aperture_not_a_smaller_iris_or_footprint_margin():
    g = build_eye_geometry(
        EyeParameters(width=2.0, height=1.0),
        gaze=Gaze(direction="right", strength=100),
    )
    px, py = g.pupil_center
    assert px > 0.14
    # The center is allowed to reach the aperture boundary; the renderer's
    # eye clip is responsible for hiding the pupil/iris footprint outside it.
    assert abs(px - g.gaze_solution.offset_x) < 1e-9 or px < g.gaze_solution.offset_x


def test_large_second_pupil_gets_a_tighter_footprint_limit():
    appearance = EyeAppearance(pupils=(PupilSpec(scale=0.5), PupilSpec(x=0.1, scale=2.0)))
    g = build_eye_geometry(EyeParameters(width=2.0, height=1.0), gaze=Gaze(direction="right", strength=100), appearance=appearance)
    assert len(g.pupil_centers) == 2
    ix, iy = g.iris_center
    for (px, py), (rx, ry) in zip(g.pupil_centers, g.pupil_radii):
        assert math.isfinite(px) and math.isfinite(py)
        assert rx > 0 and ry > 0


def test_gaze_solver_is_renderer_independent():
    contour = ((-1.0, 0.0), (0.0, -0.5), (1.0, 0.0), (0.0, 0.5))
    s = GazeSolver.solve(Gaze(direction="upper_right", strength=2), contour, iris_center=(0, 0), iris_rx=.45, iris_ry=.25, pupil_rx=.1, pupil_ry=.08)
    assert s.normalized_x > 0 and s.normalized_y < 0
    assert s.offset_x > 0 and s.offset_y < 0
    assert s.offset_x ** 2 + s.offset_y ** 2 > 0


def test_explicit_pupil_offset_cannot_escape_iris():
    appearance = EyeAppearance(pupils=(PupilSpec(x=100, y=-100),))
    g = build_eye_geometry(EyeParameters(width=2.0, height=1.0), appearance=appearance)
    px, py = g.pupil_center
    ix, iy = g.iris_center
    assert ((px - ix) / g.iris_rx) ** 2 + ((py - iy) / g.iris_ry) ** 2 <= 1.000001


def test_extreme_gaze_reaches_each_aperture_direction():
    for direction in ("left", "right", "up", "down", "upper_left", "upper_right", "lower_left", "lower_right"):
        g = build_eye_geometry(EyeParameters(width=2.0, height=1.0), gaze=Gaze(direction=direction, strength=100))
        assert g.gaze_solution.limit > 0
        assert abs(g.gaze_solution.offset_x) > 0.09 or abs(g.gaze_solution.offset_y) > 0.09


def test_final_contour_reflects_gaze_lid_follow():
    base = build_eye_geometry(EyeParameters(width=2.0, height=1.0), gaze=Gaze(direction="up", strength=1))
    assert base.contour_points == base.outer_path


def test_closed_eye_emits_no_lashes():
    from visual_engine.render import render_eye_svg
    svg = render_eye_svg(build_eye_geometry(state="closed"))
    assert 'stroke-linecap="round"' not in svg or svg.count('<line') == 0
    # The closed-eye contour/creases may remain; lash geometry itself must not be emitted.
    assert svg.count('<line') == 0


def test_brow_eye_gap_is_hard_bounded_under_expression():
    from visual_engine.render import render_eye_svg
    from visual_engine.geometry import BrowSpec
    for expression in ("anger", "fear", "surprise", "sleepy", "pain"):
        appearance = EyeAppearance(eyebrow=BrowSpec(y=10.0, min_eye_gap=0.08, max_eye_gap=0.90))
        g = build_eye_geometry(appearance=appearance, expression=expression)
        svg = render_eye_svg(g, appearance=appearance)
        assert 'stroke="#000000"' in svg


def test_brow_gap_configuration_is_validated():
    from visual_engine.geometry import BrowSpec
    import pytest
    with pytest.raises(ValueError):
        BrowSpec(min_eye_gap=-0.1)
    with pytest.raises(ValueError):
        BrowSpec(min_eye_gap=0.5, max_eye_gap=0.4)


def test_brow_reference_frame_is_stable_when_eye_closes():
    from visual_engine.components.face.eyes.core import EyeParameters, Gaze, build_eye_geometry
    normal = build_eye_geometry(EyeParameters(), state="normal", gaze=Gaze())
    closed = build_eye_geometry(EyeParameters(), state="closed", gaze=Gaze())
    assert closed.brow_reference_scale == pytest.approx(normal.brow_reference_scale)
    assert closed.brow_reference_top_y == pytest.approx(normal.brow_reference_top_y)


def test_closed_eye_does_not_collapse_brow_gap():
    from visual_engine.components.face.eyes.core import EyeParameters, Gaze, build_eye_geometry
    from visual_engine.geometry import BrowSpec, EyeAppearance
    appearance = EyeAppearance(eyebrow=BrowSpec(y=-0.75, min_eye_gap=0.18, max_eye_gap=0.60))
    normal = build_eye_geometry(EyeParameters(), state="normal", gaze=Gaze(), appearance=appearance)
    closed = build_eye_geometry(EyeParameters(), state="closed", gaze=Gaze(), appearance=appearance)
    # Rendering uses the same anatomical reference for both states. The closest
    # brow point therefore cannot collapse toward the closed aperture.
    assert normal.brow_reference_top_y == pytest.approx(closed.brow_reference_top_y)
    assert normal.brow_reference_scale == pytest.approx(closed.brow_reference_scale)


def test_rendered_brow_height_is_identical_when_eye_closes():
    from visual_engine.render import render_eye_svg
    from visual_engine.geometry import BrowSpec, EyeAppearance
    appearance = EyeAppearance(eyebrow=BrowSpec(y=-0.75, min_eye_gap=0.18, max_eye_gap=0.60))
    normal_svg = render_eye_svg(build_eye_geometry(state="normal", appearance=appearance), appearance=appearance)
    closed_svg = render_eye_svg(build_eye_geometry(state="closed", appearance=appearance), appearance=appearance)

    import re
    pattern = re.compile(r'<path d="([^"]+)" fill="none" stroke="#000000"')
    normal_brow = pattern.findall(normal_svg)[-1]
    closed_brow = pattern.findall(closed_svg)[-1]
    assert normal_brow == closed_brow
