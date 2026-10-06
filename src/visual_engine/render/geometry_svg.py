from __future__ import annotations

"""Fail-closed SVG renderer for the generic ``GeometryContract``.

This is deliberately smaller than the ocular renderer.  It renders only the
renderer-neutral primitives already required by the first production slice:
paths plus ellipses.  Unknown primitive kinds and unresolved masks are rejected
instead of being approximated, because silently dropping geometry can create a
visually plausible but semantically false artifact.

The role colors in ``GeometrySvgTheme`` are presentation defaults.  They are
not COLOR-domain transformations, conversions, palette resolution, or grading.
Canonical component appearance still comes from ``ResolvedVisualContract``.
"""

from dataclasses import dataclass
import html
import math
from typing import Mapping
from xml.etree import ElementTree as ET

from visual_engine.components.common.geometry_contract import GeometryContract, GeometryPath
from visual_engine.components.common.visual_contract import ResolvedVisualContract


@dataclass(frozen=True, slots=True)
class GeometrySvgTheme:
    """Explicit renderer presentation defaults for generic geometric roles."""

    background: str = "#ffffff"
    iris: str = "#3f6f8f"
    pupil: str = "#111111"
    reflection: str = "#ffffff"
    caruncle: str = "#d88f91"
    aperture_fill: str = "#ffffff"


@dataclass(frozen=True, slots=True)
class GeometrySvgStyle:
    """Resolved style for one component geometry owner."""

    fill: str
    contour_color: str
    contour_width: float
    contour_opacity: float
    opacity: float
    visibility: float


def _style(resolved: ResolvedVisualContract) -> GeometrySvgStyle:
    return GeometrySvgStyle(
        fill=resolved.effective_fill_color,
        contour_color=resolved.effective_contour.color,
        contour_width=resolved.effective_contour.width,
        contour_opacity=resolved.effective_contour.opacity,
        opacity=resolved.effective_visibility,
        visibility=resolved.visibility,
    )


def _path_d(path: GeometryPath) -> str:
    chunks: list[str] = []
    for command, values in path.commands:
        chunks.append(command + (" " + " ".join(f"{value:.6f}" for value in values) if values else ""))
    return " ".join(chunks)


def _surface_roles(geometry: GeometryContract) -> dict[int, tuple[str, str]]:
    """Map global path indexes to ``(role, component_id)``.

    Composite geometry uses global path indexes.  The composition layer is
    responsible for rebasing child-local surface indexes before they reach a
    renderer; this renderer therefore never guesses offsets from path counts.
    """
    roles: dict[int, tuple[str, str]] = {}
    for surface in geometry.surfaces:
        raw_index = surface.data.get("path_index")
        if raw_index is None:
            continue
        index = int(raw_index)
        component_id = str(surface.data.get("source_component_id", surface.data.get("component_id", "")))
        roles.setdefault(index, (surface.name.rsplit(":", 1)[-1], component_id))
    return roles



def _surface_depths(geometry: GeometryContract) -> dict[int, int]:
    """Return authored integer depth layers for surfaces that explicitly define one.

    Depth is optional metadata: legacy ocular surfaces keep their existing semantic
    paint priorities. When a production surface supplies ``depth_layer``, the same
    value can be consumed by the visibility proof without inventing depth for it.
    """
    depths: dict[int, int] = {}
    for surface in geometry.surfaces:
        raw_index = surface.data.get("path_index")
        raw_depth = surface.data.get("depth_layer")
        if raw_index is None or raw_depth is None:
            continue
        depth = int(raw_depth)
        if depth < 0:
            raise ValueError("surface depth_layer must be >= 0")
        depths.setdefault(int(raw_index), depth)
    return depths

def _path_element(path: GeometryPath, *, role: str, style: GeometrySvgStyle, theme: GeometrySvgTheme) -> str:
    if not path.commands:
        return ""
    closed = path.commands[-1][0] == "Z"
    fill = style.fill if role in {"ear", "hair", "head", "nose", "aperture", "medial_caruncle"} and closed else "none"
    if role == "aperture":
        fill = theme.aperture_fill
    stroke = style.contour_color
    width = style.contour_width
    if role in {"upper_crease", "lower_crease", "epicanthic_fold"}:
        width *= 0.65
    if role == "medial_caruncle":
        fill = theme.caruncle
    return (
        f'<path d="{html.escape(_path_d(path), quote=True)}" fill="{html.escape(fill, quote=True)}" '
        f'stroke="{html.escape(stroke, quote=True)}" stroke-width="{width:.6f}" '
        f'stroke-opacity="{style.contour_opacity:.6f}" opacity="{style.opacity:.6f}" '
        f'stroke-linecap="round" '
        f'stroke-linejoin="round"/>'
    )


def _primitive_element(data: Mapping[str, object], *, theme: GeometrySvgTheme, style: GeometrySvgStyle) -> str:
    role = str(data.get("role", ""))
    cx = float(data["cx"])
    cy = float(data["cy"])
    rx = float(data.get("rx", data.get("r", 0.0)))
    ry = float(data.get("ry", data.get("r", 0.0)))
    rotation = float(data.get("rotation_deg", 0.0))
    if rx <= 0.0 or ry <= 0.0 or not all(math.isfinite(v) for v in (cx, cy, rx, ry, rotation)):
        raise ValueError("ellipse primitive requires finite positive radii")
    if role == "iris":
        fill, stroke = theme.iris, style.contour_color
    elif role == "pupil":
        fill, stroke = theme.pupil, theme.pupil
    elif role == "reflection":
        fill, stroke = theme.reflection, "none"
    else:
        fill, stroke = style.fill, style.contour_color
    transform = f' transform="rotate({rotation:.6f} {cx:.6f} {cy:.6f})"' if abs(rotation) > 1e-12 else ""
    return (
        f'<ellipse cx="{cx:.6f}" cy="{cy:.6f}" rx="{rx:.6f}" ry="{ry:.6f}" '
        f'fill="{html.escape(fill, quote=True)}" stroke="{html.escape(stroke, quote=True)}" '
        f'stroke-width="{style.contour_width:.6f}" opacity="{style.opacity:.6f}"{transform}/>'
    )


def render_geometry_svg(
    geometry: GeometryContract,
    *,
    styles: Mapping[str, ResolvedVisualContract] | None = None,
    width: int = 900,
    height: int = 900,
    theme: GeometrySvgTheme | None = None,
) -> str:
    """Render one camera-space geometry contract to deterministic SVG.

    ``styles`` is keyed by the component ids carried by geometry surfaces and
    primitives.  Missing component styles fall back to the generic visual
    contract, making the renderer useful for isolated geometry while keeping
    style ownership outside the renderer.
    """
    if width <= 0 or height <= 0:
        raise ValueError("SVG dimensions must be positive")
    if geometry.masks:
        raise ValueError("generic SVG renderer does not silently approximate geometry masks")

    theme = theme or GeometrySvgTheme()
    resolved_styles = {key: _style(value) for key, value in (styles or {}).items()}
    fallback = GeometrySvgStyle("#ffffff", "#000000", 0.02, 1.0, 1.0, 1.0)
    roles = _surface_roles(geometry)
    depths = _surface_depths(geometry)

    # Geometry composition order is deterministic but not a paint-order contract:
    # the composite face generator currently stores child paths before the head.
    # Paint the structural occluder (head) first, then aperture/lid details, so
    # the renderer cannot accidentally cover the eyes merely because of merge order.
    paint_priority = {
        "ear": -10,
        "head": 0,
        "hair": 5,
        "aperture": 10,
        "upper_lid": 20,
        "lower_lid": 21,
        "upper_crease": 30,
        "lower_crease": 31,
        "epicanthic_fold": 32,
        "medial_caruncle": 40,
    }
    ordered_paths = sorted(
        enumerate(geometry.paths),
        key=lambda item: (
            depths.get(item[0], 0),
            paint_priority.get(roles.get(item[0], ("path", ""))[0], 50),
            item[0],
        ),
    )
    path_elements: list[str] = []
    for index, path in ordered_paths:
        role, component_id = roles.get(index, ("path", ""))
        style = resolved_styles.get(component_id, fallback)
        # Visibility is a semantic contract, not a hint. Do not emit geometry
        # for an owner whose resolved visibility is exactly zero; this prevents
        # hidden components from remaining visually present by accident.
        if style.visibility <= 0.0 or style.opacity <= 0.0:
            continue
        path_elements.append(_path_element(path, role=role, style=style, theme=theme))

    primitive_elements: list[str] = []
    for primitive in geometry.primitives:
        if primitive.kind != "ellipse":
            raise ValueError(f"generic SVG renderer does not support primitive {primitive.kind!r}")
        component_id = str(primitive.data.get("component_id", ""))
        style = resolved_styles.get(component_id, fallback)
        if style.visibility <= 0.0 or style.opacity <= 0.0:
            continue
        primitive_elements.append(_primitive_element(primitive.data, theme=theme, style=style))

    b = geometry.bounds
    pad = max(0.05, 0.08 * max(b.max_x - b.min_x, b.max_y - b.min_y, 1.0))
    view_box = (b.min_x - pad, b.min_y - pad, max(b.max_x - b.min_x + 2 * pad, 1.0), max(b.max_y - b.min_y + 2 * pad, 1.0))
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{int(width)}" height="{int(height)}" '
        f'viewBox="{view_box[0]:.6f} {view_box[1]:.6f} {view_box[2]:.6f} {view_box[3]:.6f}">'
        f'<rect x="{view_box[0]:.6f}" y="{view_box[1]:.6f}" width="{view_box[2]:.6f}" height="{view_box[3]:.6f}" fill="{html.escape(theme.background, quote=True)}"/>'
        + "".join(path_elements)
        + "".join(primitive_elements)
        + "</svg>"
    )
    # Validate the exact bytes we are about to return. This catches malformed XML
    # before the production boundary can publish a supposedly renderable artifact.
    ET.fromstring(svg)
    return svg
