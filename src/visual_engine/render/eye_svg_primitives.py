from __future__ import annotations
import html, math
import hashlib
from visual_engine.geometry.eye import EyeAppearance, EyeGeometry, BrowSpec, LashSpec, LowerLashSpec


def _pt(p: tuple[float, float]) -> str:
    return f"{p[0]:.6f},{p[1]:.6f}"


def _smooth_open_path(points: tuple[tuple[float, float], ...]) -> str:
    """Cubic interpolation for an open sampled curve with stable end tangents."""
    if len(points) < 2:
        raise ValueError("at least two points required")
    out = [f"M {_pt(points[0])}"]
    n = len(points)
    for i in range(n - 1):
        p0 = points[i - 1] if i > 0 else points[i]
        p1 = points[i]
        p2 = points[i + 1]
        p3 = points[i + 2] if i + 2 < n else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6.0, p1[1] + (p2[1] - p0[1]) / 6.0)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6.0, p2[1] - (p3[1] - p1[1]) / 6.0)
        out.append(f"C {_pt(c1)} {_pt(c2)} {_pt(p2)}")
    return " ".join(out)


def eye_outer_path(g: EyeGeometry, *, irregularity: float = 0.0, wave_frequency: float = 1.0) -> str:
    """Render the geometry-owned closed aperture, including C1 canthus bridges."""
    upper = g.upper_lid_points
    lower = g.lower_lid_points
    if len(upper) < 2 or len(lower) < 2:
        return _smooth_open_path(g.contour_points)
    if g.opening <= 0:
        # Closed/covered eyes intentionally use the degenerate aperture contract.
        return _smooth_open_path(g.contour_points) + " Z"

    upper_path = _smooth_open_path(upper)
    lower_path = _smooth_open_path(tuple(reversed(lower)))
    lower_rest = " ".join(lower_path.split(" ")[2:])
    # V1.7 shared-point terminals close the topology directly: there is no extra
    # stroke segment to create the old thick vertical cap. Legacy bridge terminals
    # still serialize their geometry-owned cubic exactly.
    outer = g.outer_canthus_bridge
    inner = g.inner_canthus_bridge
    outer_c = f"C {_pt(outer[1])} {_pt(outer[2])} {_pt(outer[3])}" if len(outer) == 4 else f"L {_pt(lower[0])}"
    inner_c = f"C {_pt(inner[1])} {_pt(inner[2])} {_pt(inner[3])}" if len(inner) == 4 else f"L {_pt(upper[0])}"
    return upper_path + " " + outer_c + " " + lower_rest + " " + inner_c + " Z"


def _lid_path(points: tuple[tuple[float, float], ...]) -> str:
    return _smooth_open_path(points)

def _eyebrow_svg(g: EyeGeometry, brow: BrowSpec, *, side: int = 0, visibility=None) -> str:
    """Render the brow in the eye-local anatomical frame, then inherit eye rotation.

    Gaze direction is intentionally absent from this transform. Gaze moves the
    iris/pupil assembly inside the aperture; parent/eye rotation is the rigid
    transform inherited by the brow and other ocular children.
    """
    if visibility is not None and not visibility.is_visible("eyebrow"):
        return ""
    if not brow.enabled or brow.length <= 0 or brow.thickness <= 0:
        return ""

    scale = g.brow_reference_scale
    top_boundary = g.brow_reference_top_local_y
    requested_y = brow.y * scale

    length_factor = {
        "short": .48, "long": 1.25, "thick": 1.0, "dense": 1.0,
    }.get(brow.shape, 1.0)
    half = brow.length * length_factor * g.nominal_width * 0.5
    amount = {
        "arched": .24, "high_arch": .34, "low_arch": .09, "angular": -.02,
        "straight": 0.0, "ornate": .16, "long": .10, "short": .08,
        "thick": .12, "dense": .10, "faded": .10, "inward": .08,
    }[brow.shape]

    min_gap = brow.min_eye_gap * scale
    max_gap = brow.max_eye_gap * scale
    required_gap = min_gap + max(0.0, -amount) * scale
    if required_gap > max_gap:
        raise ValueError("eyebrow gap bounds are too narrow for its morphology")
    requested_gap = top_boundary - requested_y

    # The eyebrow is a child of the ocular parent, not of the gaze vector.
    # Gaze belongs to the internal iris/pupil assembly; allowing it to translate
    # the brow made the brow drift during look directions and broke pair coherence.
    gap_after_request = top_boundary - requested_y
    gap = min(max(gap_after_request, required_gap), max_gap)
    y = top_boundary - gap

    x = brow.x
    peak = y - amount * scale

    if brow.shape == "angular":
        local_path = f"M {x-half:.6f},{y:.6f} L {x:.6f},{peak:.6f} L {x+half:.6f},{y:.6f}"
    elif brow.shape == "inward" and side in {-1, 1}:
        outer_y = y + max(scale * .015, 1e-9)
        inner_y = y - max(scale * .075, 1e-9)
        if side < 0:
            local_path = f"M {x-half:.6f},{outer_y:.6f} Q {x:.6f},{peak:.6f} {x+half:.6f},{inner_y:.6f}"
        else:
            local_path = f"M {x-half:.6f},{inner_y:.6f} Q {x:.6f},{peak:.6f} {x+half:.6f},{outer_y:.6f}"
    else:
        local_path = f"M {x-half:.6f},{y:.6f} Q {x:.6f},{peak:.6f} {x+half:.6f},{y:.6f}"

    opacity = brow.density
    if brow.shape == "faded":
        opacity *= .42
    stroke_factor = {"thick": 1.55, "dense": 1.25, "short": .95}.get(brow.shape, 1.0)
    stroke_w = brow.thickness * g.nominal_width * stroke_factor

    angle = g.rotation_deg + brow.angle_deg
    # The path is authored in an eye-local frame around (0,0). Translate that
    # local origin to the eye centre, then rotate the child with the parent. The
    # previous implementation rotated local coordinates around a world-space
    # centre without first translating them, which displaced paired brows toward
    # the middle and could make them overlap or cross.
    tx, ty = g.center_x, g.center_y
    transform = f'translate({tx:.6f} {ty:.6f}) rotate({angle:.6f})'
    path = f'<path d="{local_path}" fill="none" stroke="{html.escape(brow.color)}" stroke-width="{stroke_w:.6f}" stroke-linecap="round" stroke-linejoin="round" opacity="{opacity:.6f}" transform="{transform}"/>'
    ornaments = []
    if brow.shape == "ornate" or brow.ornament > 0:
        ornament_strength = max(brow.ornament, .45 if brow.shape == "ornate" else 0.0)
        # Ornaments are placed in the same local frame and inherit the exact eye rotation.
        for j, frac in enumerate((-.32, 0.0, .32)):
            ox = x + frac * half * 1.8
            oy = peak - max(stroke_w * (0.8 + 0.2*j) * ornament_strength, 1e-9)
            rad = max(stroke_w*.55*ornament_strength,1e-9)
            path += f'<circle cx="{ox:.6f}" cy="{oy:.6f}" r="{rad:.6f}" fill="{html.escape(brow.color)}" opacity="{opacity:.6f}" transform="{transform}"/>'
    return path

def _lash_path(x: float, y: float, dx: float, dy: float, length: float, curvature: float) -> str:
    ex, ey = x + dx * length, y + dy * length
    tx, ty = -dy, dx
    bend = curvature * length * .35
    c1 = (x + dx*length*.34 + tx*bend*.25, y + dy*length*.34 + ty*bend*.25)
    c2 = (x + dx*length*.78 + tx*bend, y + dy*length*.78 + ty*bend)
    return f"M {x:.6f},{y:.6f} C {c1[0]:.6f},{c1[1]:.6f} {c2[0]:.6f},{c2[1]:.6f} {ex:.6f},{ey:.6f}"


def _lash_tapered_path(x: float, y: float, dx: float, dy: float, length: float, width: float, curvature: float) -> str:
    """Closed elongated-cone lash: broad at the root, tapered to a point."""
    nx, ny = -dy, dx
    half = width * 0.5
    ex, ey = x + dx * length, y + dy * length
    bend = curvature * length * .28
    c1 = (x + dx*length*.38 + nx*bend, y + dy*length*.38 + ny*bend)
    c2 = (x + dx*length*.82 + nx*bend*.35, y + dy*length*.82 + ny*bend*.35)
    left = (x + nx*half, y + ny*half)
    right = (x - nx*half, y - ny*half)
    return (
        f"M {left[0]:.6f},{left[1]:.6f} "
        f"C {c1[0]+nx*half*.65:.6f},{c1[1]+ny*half*.65:.6f} "
        f"{c2[0]+nx*half*.15:.6f},{c2[1]+ny*half*.15:.6f} "
        f"{ex:.6f},{ey:.6f} "
        f"C {c2[0]-nx*half*.15:.6f},{c2[1]-ny*half*.15:.6f} "
        f"{c1[0]-nx*half*.65:.6f},{c1[1]-ny*half*.65:.6f} "
        f"{right[0]:.6f},{right[1]:.6f} Z"
    )


def _lash_svg_element(x: float, y: float, fx: float, fy: float, length: float, width: float,
                      curvature: float, color: str, opacity: float, form: str) -> str:
    if form == "line":
        ex, ey = x + fx*length, y + fy*length
        return f'<line x1="{x:.6f}" y1="{y:.6f}" x2="{ex:.6f}" y2="{ey:.6f}" stroke="{html.escape(color)}" stroke-width="{width:.6f}" stroke-linecap="round" opacity="{opacity:.6f}"/>'
    if form == "tapered":
        d = _lash_tapered_path(x, y, fx, fy, length, width, curvature)
        return f'<path d="{d}" fill="{html.escape(color)}" opacity="{opacity:.6f}"/>'
    d = _lash_path(x, y, fx, fy, length, curvature)
    return f'<path d="{d}" fill="none" stroke="{html.escape(color)}" stroke-width="{width:.6f}" stroke-linecap="round" opacity="{opacity:.6f}"/>'


def _lashes_svg(g: EyeGeometry, lashes: LashSpec, visibility=None) -> str:
    if visibility is not None and not visibility.is_visible("lashes"):
        return ""
    if g.opening <= 0 or g.state in {"closed", "covered"} or not lashes.enabled or lashes.count <= 0 or lashes.length <= 0 or len(g.upper_lid_points) < 2:
        return ""
    points = g.upper_lid_points
    parts: list[str] = []
    for i in range(lashes.count):
        t = i / (lashes.count - 1) if lashes.count > 1 else .5
        if lashes.spacing_jitter:
            jitter = ((((i * 1103515245 + 12345) >> 16) & 0x7FFF) / 32767.0 - .5) * lashes.spacing_jitter
            t = min(1.0, max(0.0, t + jitter / max(lashes.count - 1, 1)))
        # Do not plant a full lash root exactly on the medial terminal. That
        # stroke mass visually becomes a false canthus cap and can hide the
        # separate medial caruncle.
        if t < 0.045 or t > 0.875:
            continue
        idx = min(len(points)-1, max(0, round(t*(len(points)-1))))
        x, y = points[idx]
        if ((i * 9973 + 17) % 1000) / 1000.0 > lashes.density:
            continue
        corner = abs(2.0*t - 1.0)
        lateral = (2.0*t - 1.0) * (0.10 + lashes.outer_flare * corner)
        up = 1.0 + lashes.upward_bias
        if lashes.form == "disheveled":
            # Deterministic small angular variation; never changes the global outward/upward bias.
            jitter = ((((i * 2654435761 + 1013904223) >> 17) & 0x7FFF) / 32767.0 - .5) * .30
            lateral += jitter
        fx, fy = lateral, -up
        angle = math.radians(g.rotation_deg)
        fx, fy = (math.cos(angle)*fx - math.sin(angle)*fy, math.sin(angle)*fx + math.cos(angle)*fy)
        fn = max(math.hypot(fx, fy), 1e-9); fx, fy = fx/fn, fy/fn
        inner_factor = lashes.inner_length_factor + (1.0-lashes.inner_length_factor) * min(1.0, t/.22)
        style_factor = {"natural": 1.0, "anime": 1.15, "spiky": 1.30, "ornate": 1.20}[lashes.style]
        if lashes.form == "clustered":
            style_factor *= 1.05
        elif lashes.form == "disheveled":
            style_factor *= 1.02
        ll = lashes.length * max(g.visible_height, 1e-9) * inner_factor * style_factor
        curve = lashes.curvature * (1.25 if lashes.style in {"anime", "ornate"} else 1.0) * (0.75 + 0.25*(1.0-lashes.taper))
        width = lashes.thickness * g.nominal_width
        if lashes.form == "clustered":
            # Clustered lashes deliberately overlap at the root while remaining deterministic.
            width *= 1.15
        parts.append(_lash_svg_element(x, y, fx, fy, ll, width, curve, lashes.color, 1.0, lashes.form))
    return "\n".join(parts)


