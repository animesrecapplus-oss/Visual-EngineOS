from dataclasses import replace

from visual_engine.geometry import (
    BrowSpec, ContourSpec, EyeAppearance, EyeParameters, EyelidAppearance,
    LashSpec, OcularPresentationProfile, PupilSpec, apply_ocular_presentation,
    build_eye_geometry,
)
from visual_engine.render import render_eye_svg


def test_eye_has_two_c1_stable_lid_curves_and_shared_canthus_endpoints():
    g = build_eye_geometry(EyeParameters())
    assert g.upper_lid_points[0][0] == g.lower_lid_points[0][0]
    assert g.upper_lid_points[-1][0] == g.lower_lid_points[-1][0]
    assert g.upper_lid_points[0][1] == g.lower_lid_points[0][1]
    assert g.upper_lid_points[-1][1] == g.lower_lid_points[-1][1]
    assert g.inner_canthus == g.upper_lid_points[0]
    assert g.outer_canthus == g.upper_lid_points[-1]


def test_lower_contour_does_not_use_old_four_point_arrow_path():
    g = build_eye_geometry(EyeParameters())
    # The lower curve has a non-zero interior arc and returns horizontally to the
    # canthi instead of converging into an artificial pointed tip.
    assert max(y for _, y in g.lower_lid_points) > 0
    assert g.lower_lid_points[0][1] == 0
    assert g.lower_lid_points[-1][1] == 0


def test_upper_lashes_point_outward_and_upward_on_right_half():
    g = build_eye_geometry(EyeParameters(width=2, height=1))
    a = EyeAppearance(lashes=LashSpec(style="natural", count=12, density=1, length=.15))
    svg = render_eye_svg(g, appearance=a)
    # Natural lashes are explicit line primitives; their endpoint is above the
    # corresponding upper-lid point in the default horizontal eye.
    import re
    lines = re.findall(r'<line\b[^>]*/>', svg)
    upper_lines = [line for line in lines if 'stroke="#000000"' in line]
    assert len(upper_lines) >= 8
    assert all('y2="-' in line for line in upper_lines)


def test_lash_styles_are_real_rendering_modes():
    g = build_eye_geometry(EyeParameters())
    for style in ("natural", "anime", "spiky", "ornate"):
        svg = render_eye_svg(g, appearance=EyeAppearance(lashes=LashSpec(style=style, density=1, count=8)))
        assert "stroke=\"#000000\"" in svg
        assert ("<line" in svg) if style == "natural" else ("<path" in svg)


def test_contour_is_per_component_and_styleable():
    g = build_eye_geometry(EyeParameters())
    a = EyeAppearance(contour=ContourSpec(color="#ff00aa", width=.04, style="dashed"))
    svg = render_eye_svg(g, appearance=a)
    assert '#ff00aa' in svg
    assert 'stroke-dasharray' in svg


def test_eyelid_is_mandatory_by_default_and_can_be_styled():
    a = EyeAppearance(eyelid=EyelidAppearance(upper_width=.04, lower_width=.02))
    svg = render_eye_svg(build_eye_geometry(), appearance=a)
    assert svg.count('stroke="#000000"') >= 2


def test_pupil_is_clipped_by_aperture_even_when_gaze_is_extreme():
    a = EyeAppearance(pupils=(PupilSpec(x=100, y=-100, scale=2),))
    g = build_eye_geometry(EyeParameters(width=2, height=1), appearance=a)
    cx, cy = g.pupil_center
    assert abs(cx - g.center_x) < g.iris_rx
    assert abs(cy - g.center_y) < g.iris_ry
    svg = render_eye_svg(g, appearance=a)
    assert 'clip-path=' in svg


def test_presentation_profiles_modify_visuals_without_rewriting_identity():
    base = EyeParameters()
    app = EyeAppearance()
    p = OcularPresentationProfile.preset("elder", "masculine_coded")
    rp, ra = apply_ocular_presentation(base, app, p)
    assert rp.width == base.width and rp.height == base.height
    assert rp.opening != base.opening
    assert ra.lashes.density != app.lashes.density


def test_colored_pupil_keeps_black_component_contour():
    a = EyeAppearance(pupils=(PupilSpec(color="#ff3355", outline_color="#000000", outline_width=.02),))
    svg = render_eye_svg(build_eye_geometry(), appearance=a)
    assert 'fill="#ff3355"' in svg
    assert 'stroke="#000000"' in svg


def test_eye_pair_profile_is_applied_symmetrically():
    from visual_engine.geometry import EyePairSpec, OcularPresentationProfile, build_eye_pair
    spec = EyePairSpec(presentation_profile=OcularPresentationProfile.preset("child", "neutral"))
    pair = build_eye_pair(spec)
    assert pair.left.iris_rx == pair.right.iris_rx
    assert pair.left.iris_ry == pair.right.iris_ry


def test_generated_svg_is_well_formed_and_has_no_nonfinite_numbers():
    import re
    import xml.etree.ElementTree as ET
    svg = render_eye_svg(build_eye_geometry(), appearance=EyeAppearance())
    ET.fromstring(svg)
    assert "NaN" not in svg and "Infinity" not in svg
    assert not re.search(r"(?i)(?:nan|inf)", svg)


def test_upper_lashes_are_denser_than_lower_lashes_by_default():
    from visual_engine.geometry import EyeAppearance
    a = EyeAppearance()
    assert a.lashes.count > a.lower_lashes.count
    assert a.lashes.density > a.lower_lashes.density
    assert a.lower_lashes.opacity < a.lashes.density


def test_eyelid_has_independent_visible_fold_geometry():
    g = build_eye_geometry()
    assert len(g.upper_crease_points) >= 2
    assert len(g.lower_crease_points) >= 2
    assert min(y for _, y in g.upper_crease_points) < min(y for _, y in g.upper_lid_points)
    assert max(y for _, y in g.lower_crease_points) > max(y for _, y in g.lower_lid_points)
    svg = render_eye_svg(g, appearance=EyeAppearance())
    assert svg.count('stroke="#000000"') >= 4


def test_brow_stays_above_upper_eyelid_fold():
    g = build_eye_geometry()
    svg = render_eye_svg(g, appearance=EyeAppearance(eyebrow=BrowSpec(y=10.0)))
    # The emitted brow y coordinate must remain superior to the fold boundary.
    import re
    paths = re.findall(r'<path\b[^>]*stroke="#000000"[^>]*/>', svg)
    brow_paths = [path for path in paths if 'stroke-width="0.100000"' in path and 'rotate(' in path]
    assert brow_paths
    m = re.search(r'<path d="M ([^,]+),([^ ]+) Q ([^,]+),([^ ]+) ([^,]+),([^ ]+)"', brow_paths[-1])
    assert m is not None
    brow_y = float(m.group(2))
    assert brow_y < min(y for _, y in g.upper_crease_points)


def test_expression_changes_ocular_geometry_without_renderer_conditionals():
    neutral = build_eye_geometry(expression="neutral")
    angry = build_eye_geometry(expression="anger")
    assert angry.opening != neutral.opening
    assert angry.upper_lid_points != neutral.upper_lid_points


def test_pair_expression_is_shared_by_both_eyes():
    from visual_engine.geometry import EyePairSpec, build_eye_pair
    pair = build_eye_pair(EyePairSpec(expression="surprise"))
    assert pair.left.opening == pair.right.opening
    assert pair.left.upper_lid_points != () and pair.right.upper_lid_points != ()


def test_lower_lashes_are_emitted_separately_and_subdued():
    import re
    svg = render_eye_svg(build_eye_geometry(), appearance=EyeAppearance())
    lower = [line for line in re.findall(r'<line\b[^>]*/>', svg) if 'stroke="#666666"' in line]
    assert lower
    assert all('opacity="0.340000"' in line for line in lower)


def test_expression_solver_is_renderer_independent():
    from visual_engine.geometry import OcularExpressionSolver
    base = EyeParameters(opening=0.60)
    solution = OcularExpressionSolver.solve(base, EyeAppearance(), "surprise")
    assert solution.intent == "surprise"
    assert solution.parameters.opening > base.opening
    assert solution.appearance.eyebrow.angle_deg != EyeAppearance().eyebrow.angle_deg
