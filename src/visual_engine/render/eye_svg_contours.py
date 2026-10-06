from __future__ import annotations

import html
import math
from visual_engine.geometry.eye import EyeAppearance, EyeGeometry
from .eye_svg_primitives import _lid_path

def _stroke_dash(style: str, width: float) -> str:
    if style == "dashed":
        return f' stroke-dasharray="{width*2:.6f} {width*1.5:.6f}"'
    return ""


def _contour_path_element(d: str, color: str, width: float, opacity: float, c, style: str, *, cap=None) -> str:
    dash = _stroke_dash(style, width)
    if style == "tapered":
        # The full geometric taper is emitted by the caller as segmented paths.
        # This element is the fallback for zero/very small widths.
        dash = ""
    effective_cap = c.cap if cap is None else cap
    return f'<path d="{d}" fill="none" stroke="{html.escape(color)}" stroke-width="{width:.6f}" stroke-linecap="{effective_cap}" stroke-linejoin="{c.join}" opacity="{opacity:.6f}"{dash}/>'




def _cubic_point(curve, t: float):
    p0, p1, p2, p3 = curve
    u = 1.0 - t
    return (
        u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
        u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1],
    )


def _bridge_terminal_ribbon(curve, upper_width: float, lower_width: float) -> str:
    """Render an explicit finite-gap bridge as a narrow tapered ribbon.

    The stored cubic remains the authoritative C1 geometry. The old renderer
    stroked that cubic at full eyelid width, so a short bridge became a vertical
    black plug. V1.8 makes the visual envelope depend on the actual endpoint gap
    and tapers it to zero at both lid attachments; no fixed pixel thickness is used.
    """
    if len(curve) != 4:
        return ""
    gap = math.hypot(curve[3][0] - curve[0][0], curve[3][1] - curve[0][1])
    # When the finite gap is already below the local lid stroke scale, the two
    # margins visually own the terminal and a connector only creates a seam/cap.
    if gap <= 3.0 * min(upper_width, lower_width):
        return ""
    max_width = min(upper_width, lower_width, gap * 0.08)
    if max_width <= 1e-9:
        return ""
    left = []
    right = []
    samples = 25
    for i in range(samples):
        t = i / (samples - 1)
        p = _cubic_point(curve, t)
        prev = _cubic_point(curve, max(0.0, t - 1.0/(samples-1)))
        nxt = _cubic_point(curve, min(1.0, t + 1.0/(samples-1)))
        dx, dy = nxt[0] - prev[0], nxt[1] - prev[1]
        norm = math.hypot(dx, dy)
        if norm <= 1e-12:
            nx, ny = 0.0, 1.0
        else:
            nx, ny = -dy / norm, dx / norm
        # Zero at both endpoints: the lid strokes own the attachments.
        taper = math.sin(math.pi * t) ** 0.8
        half = 0.5 * max_width * taper
        left.append((p[0] + nx*half, p[1] + ny*half))
        right.append((p[0] - nx*half, p[1] - ny*half))
    points = left + list(reversed(right))
    return "M " + " L ".join(f"{x:.6f},{y:.6f}" for x, y in points) + " Z"



def _polyline_ribbon(points, width: float, *, start_width: float = 0.0, end_width: float = 0.0) -> str:
    """Create a deterministic filled ribbon around a sampled lid segment.

    The ribbon is used only at terminal neighborhoods so the full contour stroke
    can fade to a mathematical point instead of ending in a butt/round cap mass.
    """
    if len(points) < 2 or width <= 0:
        return ""
    left=[]; right=[]
    n=len(points)
    for i,p in enumerate(points):
        prev=points[max(0,i-1)]; nxt=points[min(n-1,i+1)]
        dx,dy=nxt[0]-prev[0],nxt[1]-prev[1]
        norm=math.hypot(dx,dy)
        if norm<=1e-12:
            nx,ny=0.0,1.0
        else:
            nx,ny=-dy/norm,dx/norm
        f=i/(n-1)
        local_width=start_width*(1-f)+end_width*f
        half=.5*local_width
        left.append((p[0]+nx*half,p[1]+ny*half)); right.append((p[0]-nx*half,p[1]-ny*half))
    poly=left+list(reversed(right))
    return "M "+" L ".join(f"{x:.6f},{y:.6f}" for x,y in poly)+" Z"


def _terminal_safe_lid_render(points, color: str, width: float, opacity: float, contour, style: str) -> str:
    """Render a lid with point-like terminal ownership at both canthi."""
    if len(points) < 8 or width <= 0:
        return _contour_path_element(_lid_path(points), color, width, opacity, contour, style, cap="butt")
    n=6
    middle=points[n-1:len(points)-n+1]
    parts=[]
    if len(middle)>=2:
        parts.append(_contour_path_element(_lid_path(middle), color, width, opacity, contour, style, cap="butt"))
    start=_polyline_ribbon(points[:n], width, start_width=0.0, end_width=width)
    end=_polyline_ribbon(points[-n:], width, start_width=width, end_width=0.0)
    if start: parts.append(f'<path d="{start}" fill="{html.escape(color)}" stroke="none" opacity="{opacity:.6f}"/>')
    if end: parts.append(f'<path d="{end}" fill="{html.escape(color)}" stroke="none" opacity="{opacity:.6f}"/>')
    return "".join(parts)

def _contour_svg(g: EyeGeometry, a: EyeAppearance) -> str:
    c = a.contour
    upper = _lid_path(g.upper_lid_points)
    lower = _lid_path(g.lower_lid_points)
    up_w = a.eyelid.upper_width * g.nominal_width * c.upper_width_factor
    lo_w = a.eyelid.lower_width * g.nominal_width * c.lower_width_factor
    up_color = a.eyelid.upper_color or c.color
    lo_color = a.eyelid.lower_color or c.color
    parts: list[str] = []
    if up_w > 0 and a.eyelid.upper_enabled and a.visibility.is_visible("upper_lid"):
        parts.append(_terminal_safe_lid_render(g.upper_lid_points, up_color, up_w, c.opacity*a.eyelid.upper_opacity, c, a.eyelid.upper_style or c.style))
        if c.style == "double":
            inner = c.secondary_color or up_color
            parts.append(_terminal_safe_lid_render(g.upper_lid_points, inner, up_w*.48, c.opacity*a.eyelid.upper_opacity, c, "solid"))
    if lo_w > 0 and a.eyelid.lower_enabled and a.visibility.is_visible("lower_lid"):
        parts.append(_terminal_safe_lid_render(g.lower_lid_points, lo_color, lo_w, c.opacity*a.eyelid.lower_opacity, c, a.eyelid.lower_style or c.style))
        if c.style == "double":
            inner = c.secondary_color or lo_color
            parts.append(_terminal_safe_lid_render(g.lower_lid_points, inner, lo_w*.48, c.opacity*a.eyelid.lower_opacity, c, "solid"))
    canthus_w = max(up_w, lo_w)
    # The bridge is still the exact stored cubic, but its visual envelope is now
    # a gap-aware tapered ribbon. Full-width stroking was the source of the V1.7
    # legacy close-up caps.
    if canthus_w > 0 and a.visibility.is_visible("canthi"):
        for bridge, color in ((g.outer_canthus_bridge, up_color), (g.inner_canthus_bridge, lo_color)):
            if len(bridge) == 4:
                d = _bridge_terminal_ribbon(bridge, up_w, lo_w)
                if d:
                    parts.append(f'<path d="{d}" fill="{html.escape(color)}" stroke="none" opacity="{c.opacity:.6f}"/>')
    return "".join(parts)


def _medial_details_svg(g: EyeGeometry, a: EyeAppearance, clip_id: str) -> str:
    """Render medial details behind the lid margins and clipped to the aperture.

    V1.8 makes the layering explicit: the pale caruncle/medial fold belongs
    underneath the black canthal borders. Rendering either detail after the lid
    stroke makes it visually sit *on* the border, which is the artifact observed
    in the V1.7 close-ups.
    """
    parts: list[str] = []
    if a.visibility.is_visible("medial_caruncle") and g.medial_caruncle_points and len(g.medial_caruncle_points) >= 3:
        d = _lid_path(g.medial_caruncle_points) + " Z"
        parts.append(f'<path d="{d}" fill="{html.escape(a.caruncle.color)}" stroke="none" opacity="{a.caruncle.opacity:.6f}"/>')
    if a.visibility.is_visible("epicanthic_fold") and g.epicanthic_fold_points and len(g.epicanthic_fold_points) >= 2:
        c = a.contour
        parts.append(_contour_path_element(_lid_path(g.epicanthic_fold_points), c.color, max(c.width * g.nominal_width * .32, 1e-9), c.opacity * .42, c, "solid", cap="butt"))
    if not parts:
        return ""
    return f'<g clip-path="url(#{clip_id})">{"".join(parts)}</g>'


def _state_effects_svg(g: EyeGeometry) -> str:
    if g.state not in {"irritated", "damaged", "crying"}:
        return ""
    if not g.contour_points:
        return ""
    min_x = min(x for x,_ in g.contour_points); max_x = max(x for x,_ in g.contour_points)
    min_y = min(y for _,y in g.contour_points); max_y = max(y for _,y in g.contour_points)
    w, h = max_x-min_x, max_y-min_y
    effects = []
    if g.state in {"irritated", "damaged"}:
        effects.append(f'<ellipse cx="{g.center_x:.6f}" cy="{g.center_y+h*.12:.6f}" rx="{w*.34:.6f}" ry="{max(h*.20,1e-9):.6f}" fill="#d44" opacity="0.16"/>')
    if g.state == "damaged":
        effects.append(f'<path d="M {g.center_x-w*.22:.6f},{g.center_y+h*.02:.6f} L {g.center_x-w*.06:.6f},{g.center_y-h*.04:.6f} L {g.center_x+w*.08:.6f},{g.center_y+h*.06:.6f}" fill="none" stroke="#8b1e1e" stroke-width="{max(w*.018,1e-9):.6f}" opacity="0.7"/>')
    if g.state == "crying":
        x = g.center_x + w*.22; y0 = g.center_y + h*.24; y1 = g.center_y + h*.72
        effects.append(f'<path d="M {x:.6f},{y0:.6f} C {x-w*.04:.6f},{y0+h*.18:.6f} {x+w*.04:.6f},{y0+h*.34:.6f} {x:.6f},{y1:.6f}" fill="none" stroke="#8fd8ff" stroke-width="{max(w*.025,1e-9):.6f}" stroke-linecap="round" opacity="0.78"/>')
        effects.append(f'<ellipse cx="{x:.6f}" cy="{y1+h*.06:.6f}" rx="{max(w*.045,1e-9):.6f}" ry="{max(h*.08,1e-9):.6f}" fill="#bdeaff" opacity="0.82"/>')
    return "".join(effects)

