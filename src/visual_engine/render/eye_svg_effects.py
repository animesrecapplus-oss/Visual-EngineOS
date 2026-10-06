from __future__ import annotations

import hashlib, html, math
from visual_engine.geometry.eye import EyeAppearance, EyeGeometry
from .eye_svg_primitives import _lid_path, _lash_svg_element
from .eye_svg_contours import _contour_path_element


def _poly(points):
    if not points:
        return ""
    return "M " + " L ".join(f"{x:.6f},{y:.6f}" for x, y in points) + " Z"


def _spherical_internals(g, a):
    """Render projected ocular surfaces; geometry remains owned by the eye domain."""
    sa = g.spherical_assembly
    if sa is None:
        return ""
    parts = []
    if sa.visibility.cornea != "hidden" and sa.cornea_outline:
        parts.append(f'<path d="{_poly(sa.cornea_outline)}" fill="none" stroke="{html.escape(a.iris.outline_color)}" stroke-width="{max(g.iris_rx,g.iris_ry)*.025:.6f}" opacity="{a.iris.opacity*.35:.6f}"/>')
    if sa.visibility.iris != "hidden" and sa.iris_outline:
        parts.append(f'<path d="{_poly(sa.iris_outline)}" fill="{html.escape(a.iris.color)}" stroke="{html.escape(a.iris.outline_color)}" stroke-width="{max(g.iris_rx,g.iris_ry)*a.iris.outline_width:.6f}" opacity="{a.iris.opacity:.6f}"/>')
    if sa.visibility.pupil != "hidden" and sa.pupil_outlines:
        for index, outline in enumerate(sa.pupil_outlines):
            if index >= len(a.pupils) or not outline:
                continue
            spec = a.pupils[index]
            parts.append(f'<path d="{_poly(outline)}" fill="{html.escape(spec.color)}" stroke="{html.escape(spec.outline_color)}" stroke-width="{max(g.iris_rx,g.iris_ry)*spec.outline_width:.6f}" opacity="{spec.opacity:.6f}"/>')
    return "".join(parts)

def _lower_lashes_svg(g: EyeGeometry, lashes: LowerLashSpec, visibility=None) -> str:
    if visibility is not None and not visibility.is_visible("lower_lashes"):
        return ""
    if g.opening <= 0 or g.state in {"closed", "covered"} or not lashes.enabled or lashes.count <= 0 or lashes.length <= 0 or len(g.lower_lid_points) < 2:
        return ""
    points = g.lower_lid_points
    parts: list[str] = []
    for i in range(lashes.count):
        t = i / (lashes.count - 1) if lashes.count > 1 else .5
        if t < 0.045 or t > 0.875:
            continue
        idx = min(len(points)-1, max(0, round(t*(len(points)-1))))
        x, y = points[idx]
        if ((i * 12289 + 31) % 1000) / 1000.0 > lashes.density:
            continue
        corner = abs(2.0*t - 1.0)
        lateral = (2.0*t - 1.0) * (0.035 + lashes.outer_flare * corner)
        down = 1.0 + lashes.downward_bias
        if lashes.form == "disheveled":
            jitter = ((((i * 2654435761 + 1013904223) >> 17) & 0x7FFF) / 32767.0 - .5) * .20
            lateral += jitter
        fx, fy = lateral, down
        angle = math.radians(g.rotation_deg)
        fx, fy = (math.cos(angle)*fx - math.sin(angle)*fy, math.sin(angle)*fx + math.cos(angle)*fy)
        norm = max(math.hypot(fx, fy), 1e-9); fx, fy = fx/norm, fy/norm
        inner_factor = .55 + .45 * min(1.0, t/.20)
        if t > .80:
            inner_factor = .82 + .18 * ((t-.80)/.20)
        style_factor = 1.0 if lashes.style == "natural" else (1.08 if lashes.style == "anime" else 1.16)
        ll = lashes.length * max(g.visible_height, 1e-9) * inner_factor * style_factor
        width = lashes.thickness * g.nominal_width
        opacity = lashes.opacity
        if lashes.style == "spiky":
            opacity = min(1.0, opacity * 1.08)
        if lashes.form == "clustered":
            width *= 1.12
        parts.append(_lash_svg_element(x, y, fx, fy, ll, width, lashes.curvature, lashes.color, opacity, lashes.form))
    if not parts and lashes.count >= 3 and lashes.density > 0:
        i = lashes.count // 2
        t = i / (lashes.count - 1)
        idx = min(len(points)-1, max(0, round(t*(len(points)-1))))
        x, y = points[idx]
        parts.append(_lash_svg_element(x, y, 0.0, 1.0, lashes.length * max(g.visible_height, 1e-9) * .55, lashes.thickness * g.nominal_width, lashes.curvature, lashes.color, lashes.opacity, lashes.form))
    return "\n".join(parts)


def _lash_shadow_svg(g: EyeGeometry, a: EyeAppearance, clip_id: str | None = None) -> str:
    """Render the continuous upper-lash shadow cast onto the exposed sclera."""
    shadow = a.lash_shadow
    lashes = a.lashes
    if g.opening <= 0 or g.state in {"closed", "covered"} or not shadow.enabled or not lashes.enabled or lashes.count <= 0 or len(g.upper_lid_points) < 2:
        return ""
    density = max(0.0, min(1.0, lashes.density))
    thickness_norm = max(0.0, min(1.0, lashes.thickness / .035))
    length_norm = max(0.0, min(1.0, lashes.length / .20))
    strength = min(1.0, shadow.opacity * (.10 + density*shadow.density_response + thickness_norm*shadow.thickness_response + length_norm*shadow.length_response))
    if strength <= 0:
        return ""
    width = max(g.nominal_width * (.018 + shadow.spread + thickness_norm*.018 + length_norm*.010), 1e-9)
    offset = shadow.offset * max(g.visible_height, 1e-9)
    points = tuple((x, y + offset) for x, y in g.upper_lid_points)
    d = _lid_path(points)
    fid = "lash-shadow-filter-" + hashlib.sha1(f"{g.center_x:.6f}|{g.center_y:.6f}|{width:.6f}".encode("ascii")).hexdigest()[:10]
    blur = max(shadow.blur * g.nominal_width, 1e-9)
    clip_attr = f' clip-path="url(#{clip_id})"' if clip_id else ""
    return (f'<defs><filter id="{fid}" x="-30%" y="-100%" width="160%" height="300%">'
            f'<feGaussianBlur stdDeviation="{blur:.6f}"/></filter></defs>'
            f'<path d="{d}" fill="none" stroke="{html.escape(shadow.color)}" stroke-width="{width:.6f}" '
            f'stroke-linecap="round" opacity="{strength:.6f}" filter="url(#{fid})"{clip_attr}/>')


def _pupil_effects_svg(cx: float, cy: float, rx: float, ry: float, spec) -> str:
    parts: list[str] = []
    glow = spec.glow
    if glow.enabled and glow.intensity > 0:
        fid = "pupil-glow-" + hashlib.sha1(f"{cx:.6f}|{cy:.6f}|{rx:.6f}|{ry:.6f}|{glow.color}".encode("ascii")).hexdigest()[:10]
        std = max(glow.blur * max(rx, ry), 1e-9)
        parts.append(f'<defs><filter id="{fid}" x="-200%" y="-200%" width="400%" height="400%"><feGaussianBlur stdDeviation="{std:.6f}"/></filter></defs>')
        parts.append(f'<ellipse cx="{cx:.6f}" cy="{cy:.6f}" rx="{rx*glow.radius:.6f}" ry="{ry*glow.radius:.6f}" fill="{html.escape(glow.color)}" opacity="{glow.intensity:.6f}" filter="url(#{fid})"/>')
        if glow.core_intensity > 0:
            parts.append(f'<ellipse cx="{cx:.6f}" cy="{cy:.6f}" rx="{rx*glow.core_radius:.6f}" ry="{ry*glow.core_radius:.6f}" fill="{html.escape(glow.color)}" opacity="{glow.core_intensity:.6f}"/>')
    smoke = spec.smoke
    if smoke.enabled and smoke.opacity > 0:
        # Smoke intentionally starts at the pupil and extends beyond it. It is
        # not clipped to the pupil, only to the eye aperture by the caller.
        ang = math.radians(smoke.direction_deg)
        dx, dy = math.cos(ang), math.sin(ang)
        base = max(rx, ry)
        for i in range(smoke.wisps):
            phase = (i - (smoke.wisps-1)/2) * smoke.width * .75
            length = smoke.length * base
            bend = smoke.curl * length * (1 if i % 2 == 0 else -1)
            # Start at the pupil boundary, not at its centre. The pupil fill is
            # rendered afterwards, so a centre-origin smoke path would be hidden
            # completely. The ellipse-ray intersection gives a direction-safe
            # launch point for upward, diagonal or horizontal smoke.
            edge = 1.0 / max(math.sqrt((dx/max(rx,1e-9))**2 + (dy/max(ry,1e-9))**2), 1e-9)
            launch = edge * .92
            sx = cx + dx * launch - dy * phase
            sy = cy + dy * launch + dx * phase
            c1 = (sx + dx*length*.28 - dy*bend*.25, sy + dy*length*.28 + dx*bend*.25)
            c2 = (sx + dx*length*.70 - dy*bend, sy + dy*length*.70 + dx*bend)
            ex, ey = sx + dx*length, sy + dy*length
            op = max(0.0, smoke.opacity * (1.0 - .18*abs(phase)/max(smoke.width, 1e-9)))
            # A second, softer under-stroke makes low-resolution raster previews
            # retain the smoke instead of losing a single subpixel hairline.
            soft_w = max(smoke.width * base * 2.8, .008)
            hard_w = max(smoke.width * base * 1.25, .004)
            path = f'M {sx:.6f},{sy:.6f} C {c1[0]:.6f},{c1[1]:.6f} {c2[0]:.6f},{c2[1]:.6f} {ex:.6f},{ey:.6f}'
            parts.append(f'<path d="{path}" fill="none" stroke="{html.escape(smoke.color)}" stroke-width="{soft_w:.6f}" stroke-linecap="round" opacity="{op*.35:.6f}"/>')
            parts.append(f'<path d="{path}" fill="none" stroke="{html.escape(smoke.color)}" stroke-width="{hard_w:.6f}" stroke-linecap="round" opacity="{op:.6f}"/>')
    return "".join(parts)


def _eyelid_creases_svg(g: EyeGeometry, a: EyeAppearance) -> str:
    """Render visible lid folds separately from the aperture boundary."""
    e = a.eyelid
    parts: list[str] = []
    if e.upper_crease_enabled and a.visibility.is_visible("upper_crease") and e.upper_crease_width > 0 and len(g.upper_crease_points) >= 2:
        parts.append(_contour_path_element(
            _lid_path(g.upper_crease_points), e.crease_color,
            e.upper_crease_width * g.nominal_width, e.upper_crease_opacity,
            a.contour, "solid"
        ))
    if e.lower_crease_enabled and a.visibility.is_visible("lower_crease") and e.lower_crease_width > 0 and len(g.lower_crease_points) >= 2:
        parts.append(_contour_path_element(
            _lid_path(g.lower_crease_points), e.crease_color,
            e.lower_crease_width * g.nominal_width, e.lower_crease_opacity,
            a.contour, "solid"
        ))
    return "".join(parts)


def _iris_svg(g: EyeGeometry, a: EyeAppearance) -> str:
    if not a.visibility.is_visible("iris"):
        return ""
    iris = a.iris
    rx, ry = g.iris_rx, g.iris_ry
    fill = iris.color
    if iris.shape == "circle" and abs(rx-ry) <= 1e-12 and abs(g.iris_rotation_deg) <= 1e-12:
        base = f'<circle cx="{g.iris_center[0]:.6f}" cy="{g.iris_center[1]:.6f}" r="{rx:.6f}" fill="{html.escape(fill)}" stroke="{html.escape(iris.outline_color)}" stroke-width="{iris.outline_width*rx:.6f}" opacity="{iris.opacity:.6f}"/>'
    elif iris.shape in {"circle", "ellipse"}:
        base = f'<ellipse cx="{g.iris_center[0]:.6f}" cy="{g.iris_center[1]:.6f}" rx="{rx:.6f}" ry="{ry:.6f}" fill="{html.escape(fill)}" stroke="{html.escape(iris.outline_color)}" stroke-width="{iris.outline_width*min(rx,ry):.6f}" opacity="{iris.opacity:.6f}" transform="rotate({g.iris_rotation_deg:.6f} {g.iris_center[0]:.6f} {g.iris_center[1]:.6f})"/>'
    else:
        count = 6 if iris.shape == "hexagon" else 8
        pts = " ".join(f"{g.iris_center[0] + rx*math.cos(2*math.pi*i/count):.6f},{g.iris_center[1] + ry*math.sin(2*math.pi*i/count):.6f}" for i in range(count))
        base = f'<polygon points="{pts}" fill="{html.escape(fill)}" stroke="{html.escape(iris.outline_color)}" stroke-width="{iris.outline_width*min(rx,ry):.6f}" opacity="{iris.opacity:.6f}"/>'
    rings = "".join(
        f'<ellipse cx="{g.iris_center[0]:.6f}" cy="{g.iris_center[1]:.6f}" rx="{rx*(1-i/(iris.ring_count+1)*.18):.6f}" ry="{ry*(1-i/(iris.ring_count+1)*.18):.6f}" fill="none" stroke="{html.escape(iris.outer_color or iris.color)}" stroke-width="{max(rx,1e-9)*.035:.6f}" opacity="{iris.pattern_strength if iris.pattern_strength else .65:.6f}" transform="rotate({g.iris_rotation_deg:.6f} {g.iris_center[0]:.6f} {g.iris_center[1]:.6f})"/>'
        for i in range(iris.ring_count)
    )
    patterns = ""
    if iris.pattern in {"radial", "spokes"} and iris.pattern_strength > 0:
        count = iris.pattern_count
        for i in range(count):
            a0 = 2*math.pi*i/count
            x2 = g.iris_center[0] + rx*math.cos(a0); y2 = g.iris_center[1] + ry*math.sin(a0)
            patterns += f'<line x1="{g.iris_center[0]:.6f}" y1="{g.iris_center[1]:.6f}" x2="{x2:.6f}" y2="{y2:.6f}" stroke="{html.escape(iris.inner_color or iris.outer_color or iris.color)}" stroke-width="{max(rx,1e-9)*.018:.6f}" opacity="{iris.pattern_strength:.6f}" transform="rotate({g.iris_rotation_deg:.6f} {g.iris_center[0]:.6f} {g.iris_center[1]:.6f})"/>'
    glow = f'<ellipse cx="{g.iris_center[0]:.6f}" cy="{g.iris_center[1]:.6f}" rx="{rx*.9:.6f}" ry="{ry*.9:.6f}" fill="{html.escape(iris.inner_color or iris.color)}" opacity="{iris.glow*.22:.6f}" transform="rotate({g.iris_rotation_deg:.6f} {g.iris_center[0]:.6f} {g.iris_center[1]:.6f})"/>' if iris.glow else ""
    return base + patterns + rings + glow


def _pupil_svg(cx: float, cy: float, rx: float, ry: float, spec, *, parent_rotation_deg: float = 0.0) -> str:
    parts = [_pupil_effects_svg(cx, cy, rx, ry, spec)]
    if spec.shape == "diamond":
        points = f"{cx:.6f},{cy-ry:.6f} {cx+rx:.6f},{cy:.6f} {cx:.6f},{cy+ry:.6f} {cx-rx:.6f},{cy:.6f}"
        parts.append(f'<polygon points="{points}" fill="{html.escape(spec.color)}" stroke="{html.escape(spec.outline_color)}" stroke-width="{spec.outline_width*max(rx,ry):.6f}" opacity="{spec.opacity:.6f}" transform="rotate({parent_rotation_deg:.6f} {cx:.6f} {cy:.6f})"/>')
    else:
        if spec.shape == "vertical":
            rx *= .55
        elif spec.shape == "horizontal":
            ry *= .55
        parts.append(f'<ellipse cx="{cx:.6f}" cy="{cy:.6f}" rx="{rx:.6f}" ry="{ry:.6f}" fill="{html.escape(spec.color)}" stroke="{html.escape(spec.outline_color)}" stroke-width="{spec.outline_width*max(rx,ry):.6f}" opacity="{spec.opacity:.6f}" transform="rotate({parent_rotation_deg:.6f} {cx:.6f} {cy:.6f})"/>')
    return "".join(parts)


def _reflection_marks_svg(g: EyeGeometry, a: EyeAppearance) -> str:
    """Render structured vector highlights; no raw SVG is accepted from data."""
    parts: list[str] = []
    if not a.visibility.is_visible("reflection_marks"):
        return ""
    for i, mark in enumerate(a.reflection_marks):
        # Reflection marks are iris children. Their origin must therefore follow
        # the resolved iris parent, especially after V1.14 spherical yaw/pitch.
        cx = g.iris_center[0] + mark.x * g.iris_rx
        cy = g.iris_center[1] + mark.y * g.iris_ry
        w = mark.width * min(g.iris_rx, g.iris_ry)
        h = mark.height * min(g.iris_rx, g.iris_ry)
        common = f'fill="{html.escape(mark.color)}" opacity="{mark.opacity:.6f}"'
        if mark.shape == "circle":
            parts.append(f'<circle cx="{cx:.6f}" cy="{cy:.6f}" r="{max(w,h):.6f}" {common}/>')
        elif mark.shape == "ellipse":
            parts.append(f'<ellipse cx="{cx:.6f}" cy="{cy:.6f}" rx="{w:.6f}" ry="{h:.6f}" {common} transform="rotate({mark.rotation_deg:.6f} {cx:.6f} {cy:.6f})"/>')
        elif mark.shape == "diamond":
            pts = f"{cx:.6f},{cy-h:.6f} {cx+w:.6f},{cy:.6f} {cx:.6f},{cy+h:.6f} {cx-w:.6f},{cy:.6f}"
            parts.append(f'<polygon points="{pts}" {common} transform="rotate({mark.rotation_deg:.6f} {cx:.6f} {cy:.6f})"/>')
        else:
            parts.append(f'<rect x="{cx-w:.6f}" y="{cy-h:.6f}" width="{2*w:.6f}" height="{2*h:.6f}" rx="{min(w,h):.6f}" {common} transform="rotate({mark.rotation_deg:.6f} {cx:.6f} {cy:.6f})"/>')
    return "".join(parts)


