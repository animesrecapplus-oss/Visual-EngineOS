"""Public SVG renderer facade.

Document assembly only: geometry and visibility decisions are already resolved by
the eye domain contracts.
"""

import hashlib
import html

from visual_engine.geometry.eye import EyeAppearance, EyeGeometry
from visual_engine.geometry.eye_pair import EyePairGeometry
from .eye_svg_primitives import eye_outer_path, _eyebrow_svg, _lashes_svg
from .eye_svg_effects import _lash_shadow_svg, _lower_lashes_svg, _eyelid_creases_svg, _iris_svg, _pupil_svg, _reflection_marks_svg, _spherical_internals
from .eye_svg_contours import _contour_svg, _medial_details_svg, _state_effects_svg


def _internals(g, a, clip_id):
    if g.opening <= 0 or g.state == "covered":
        return ""
    pupils = ""
    if a.visibility.is_visible("pupil"):
        pupils = "".join(
            _pupil_svg(px, py, prx, pry, spec, parent_rotation_deg=rot)
            for (px, py), (prx, pry), spec, rot in zip(g.pupil_centers, g.pupil_radii, a.pupils, g.pupil_rotation_degs)
        )
    spots = ""
    if a.visibility.is_visible("sclera_spots"):
        spots = "".join(
            f'<circle cx="{g.center_x+x*g.nominal_width:.6f}" cy="{g.center_y+y*g.visible_height:.6f}" '
            f'r="{r*g.nominal_width:.6f}" fill="{html.escape(c)}"/>'
            for x, y, r, c in a.sclera_spots
        )
    reflection = (
        f'<ellipse cx="{g.reflection_center[0]:.6f}" cy="{g.reflection_center[1]:.6f}" '
        f'rx="{g.reflection_rx:.6f}" ry="{g.reflection_ry:.6f}" fill="{html.escape(a.reflection)}" opacity="{a.reflection_opacity:.6f}" '
        f'transform="rotate({g.reflection_rotation_deg:.6f} {g.reflection_center[0]:.6f} {g.reflection_center[1]:.6f})"/>'
        if a.visibility.is_visible("reflection") else ""
    )
    if g.spherical_assembly is not None:
        spherical = _spherical_internals(g, a)
        # The projected spherical iris/pupil replaces the legacy ellipse only for
        # non-front V1.13 poses. The existing clip still belongs to the eyelid
        # aperture, so globe and eyelid remain separate geometry owners.
        return f'<g clip-path="url(#{clip_id})">{spots}{spherical}{reflection}{_reflection_marks_svg(g,a)}</g>'
    return f'<g clip-path="url(#{clip_id})">{spots}{_iris_svg(g,a)}{pupils}{reflection}{_reflection_marks_svg(g,a)}</g>'


def render_eye_svg(g: EyeGeometry, *, appearance: EyeAppearance | None = None, width=800, height=500, background="#111111") -> str:
    a = appearance or EyeAppearance()
    path = eye_outer_path(g)
    xs = [x for x, _ in g.contour_points]
    ys = [y for _, y in g.contour_points]
    pad = max(1.0, .16 * max(max(xs)-min(xs), max(ys)-min(ys)))
    min_x, max_x, min_y, max_y = min(xs)-pad, max(xs)+pad, min(ys)-pad, max(ys)+pad
    vb_w, vb_h = max_x-min_x, max_y-min_y
    clip_key = f"{g.center_x:.6f}|{g.center_y:.6f}|{g.nominal_width:.6f}|{g.visible_height:.6f}|{g.rotation_deg:.6f}"
    clip_id = "eye-clip-" + hashlib.sha1(clip_key.encode("ascii")).hexdigest()[:12]
    marks = ""
    if a.visibility.is_visible("under_eye_marks"):
        marks = "".join(
            f'<line x1="{g.center_x+x*g.nominal_width:.6f}" y1="{g.center_y+y*g.visible_height:.6f}" '
            f'x2="{g.center_x+(x+length)*g.nominal_width:.6f}" y2="{g.center_y+y*g.visible_height:.6f}" '
            f'stroke="{html.escape(c)}" stroke-width="{thickness*g.nominal_width:.6f}" stroke-linecap="round" opacity="{a.stress_intensity:.6f}"/>'
            for x, y, length, thickness, c in a.under_eye_marks
        )
    contour_svg = _contour_svg(g,a)
    if g.spherical_assembly is not None:
        # V1.15: the lid margin is a foreground occluder for spherical children.
        body = f'{_medial_details_svg(g,a,clip_id)}{_lash_shadow_svg(g,a,clip_id)}{_eyelid_creases_svg(g,a)}{_internals(g,a,clip_id)}{contour_svg}'
    else:
        body = f'{_medial_details_svg(g,a,clip_id)}{contour_svg}{_lash_shadow_svg(g,a,clip_id)}{_eyelid_creases_svg(g,a)}{_internals(g,a,clip_id)}'
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{min_x:.6f} {min_y:.6f} {vb_w:.6f} {vb_h:.6f}"><rect x="{min_x:.6f}" y="{min_y:.6f}" width="{vb_w:.6f}" height="{vb_h:.6f}" fill="{html.escape(background)}"/><defs><clipPath id="{clip_id}"><path d="{path}"/></clipPath></defs><path d="{path}" fill="{html.escape(a.sclera)}"/>{body}{_state_effects_svg(g)}{marks}{_lashes_svg(g,a.lashes,a.visibility)}{_lower_lashes_svg(g,a.lower_lashes,a.visibility)}{_eyebrow_svg(g,a.eyebrow,visibility=a.visibility)}</svg>'''


def render_eye_pair_svg(pair: EyePairGeometry, *, width: int = 1200, height: int = 600, background="#ffffff") -> str:
    eyes = (pair.left, pair.right)
    all_points = [p for eye in eyes for p in eye.contour_points]
    min_x = min(x for x, _ in all_points); max_x = max(x for x, _ in all_points)
    min_y = min(y for _, y in all_points); max_y = max(y for _, y in all_points)
    pad = max(1.0, .18 * max(max_x-min_x, max_y-min_y))
    vb = (min_x-pad, min_y-pad, max_x-min_x+2*pad, max_y-min_y+2*pad)
    groups = []
    for idx, (g, a) in enumerate(((pair.left, pair.left_appearance), (pair.right, pair.right_appearance))):
        path = eye_outer_path(g)
        clip_id = f"pair-eye-clip-{idx}"
        contour_svg = _contour_svg(g,a)
        if g.spherical_assembly is not None:
            body = f'{_medial_details_svg(g,a,clip_id)}{_lash_shadow_svg(g,a,clip_id)}{_eyelid_creases_svg(g,a)}{_internals(g,a,clip_id)}{contour_svg}'
        else:
            body = f'{_medial_details_svg(g,a,clip_id)}{contour_svg}{_lash_shadow_svg(g,a,clip_id)}{_eyelid_creases_svg(g,a)}{_internals(g,a,clip_id)}'
        groups.append(
            f'<g><defs><clipPath id="{clip_id}"><path d="{path}"/></clipPath></defs>'
            f'<path d="{path}" fill="{html.escape(a.sclera)}"/>{body}'
            f'{_state_effects_svg(g)}{_lashes_svg(g,a.lashes,a.visibility)}'
            f'{_lower_lashes_svg(g,a.lower_lashes,a.visibility)}'
            f'{_eyebrow_svg(g,a.eyebrow,side=(-1 if idx == 0 else 1),visibility=a.visibility)}</g>'
        )
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{vb[0]:.6f} {vb[1]:.6f} {vb[2]:.6f} {vb[3]:.6f}"><rect x="{vb[0]:.6f}" y="{vb[1]:.6f}" width="{vb[2]:.6f}" height="{vb[3]:.6f}" fill="{html.escape(background)}"/>{"".join(groups)}</svg>'
