from __future__ import annotations

"""Renderer-neutral production geometry for one HumanFace hair silhouette and detail."""

import math

from visual_engine.components.common.geometry_contract import GeometryBounds, GeometryContract, GeometryPath, GeometrySurface
from visual_engine.components.common.meta import Component
from visual_engine.runtime.generators import RegisteredGeometryGenerator

HAIR_GEOMETRY_GENERATOR = "face.hair"
HAIR_GEOMETRY_GENERATOR_VERSION = "2"


def _value(component: Component, name: str, default: float) -> float:
    parameter = component.parameters.get(name)
    return default if parameter is None else float(parameter.value)


def generate_hair_geometry(component: Component, inputs=None) -> GeometryContract:
    """Generate a tapered finite silhouette with bounded optional detail strokes."""
    if inputs is not None:
        raise TypeError("face.hair generator does not accept custom inputs")
    width = _value(component, "width", 1.08)
    height = _value(component, "height", 0.72)
    hairline_depth = _value(component, "hairline_depth", 0.10)
    strand_density = _value(component, "strand_density", 0.65)
    anchor = component.anchors.get("center")
    cx = 0.0 if anchor is None else float(anchor.x)
    cy = -0.34 if anchor is None else float(anchor.y)
    if not all(math.isfinite(value) for value in (width, height, hairline_depth, strand_density, cx, cy)) or width <= 0.0 or height <= 0.0 or not 0.0 < hairline_depth <= 0.35 or not 0.0 <= strand_density <= 1.0:
        raise ValueError("hair width and height must be positive")
    half = 0.5 * width
    top = cy - 0.5 * height
    hairline = cy + 0.18 * height
    # The side contour tapers toward the temples instead of dropping as a cap.
    # The lower contour then forms a shallow central fringe and two temple dips.
    side = 0.92 * half
    fringe = hairline_depth * height
    commands = (
        ("M", (cx - side, hairline)),
        ("C", (cx - 0.98 * half, cy - 0.28 * height, cx - 0.72 * half, top, cx - 0.16 * half, top - 0.02 * height)),
        ("C", (cx + 0.20 * half, top - 0.04 * height, cx + 0.66 * half, top + 0.02 * height, cx + 0.92 * half, cy - 0.26 * height)),
        ("C", (cx + 0.98 * half, cy - 0.05 * height, cx + side, hairline - 0.01 * height, cx + side, hairline)),
        ("C", (cx + 0.98 * half, hairline + 0.10 * height, cx + 1.02 * half, hairline + 0.30 * height, cx + 1.02 * half, hairline + 0.42 * height)),
        ("C", (cx + 0.90 * half, hairline + 0.32 * height, cx + 0.66 * half, hairline + 0.10 * height, cx + 0.48 * half, hairline + 0.02 * height)),
        ("C", (cx + 0.32 * half, hairline + 0.00 * height, cx + 0.18 * half, hairline + 0.02 * height, cx, hairline + fringe)),
        ("C", (cx - 0.18 * half, hairline + 0.02 * height, cx - 0.32 * half, hairline + 0.00 * height, cx - 0.48 * half, hairline + 0.02 * height)),
        ("C", (cx - 0.66 * half, hairline + 0.10 * height, cx - 0.90 * half, hairline + 0.32 * height, cx - 1.02 * half, hairline + 0.42 * height)),
        ("C", (cx - 1.02 * half, hairline + 0.30 * height, cx - 0.98 * half, hairline + 0.10 * height, cx - side, hairline)),
        ("Z", ()),
    )
    paths = [GeometryPath(commands)]
    surfaces = [GeometrySurface("hair", {
        "path_index": 0, "semantic_region": "HAIR", "depth_layer": 1, "component_id": component.id,
    })]
    # A few optional open strands break the solid silhouette without pretending
    # to model individual follicles.  Density is a visual-detail control only.
    strand_count = round(4.0 * strand_density)
    for index in range(strand_count):
        x = cx + (-0.34 + 0.23 * index) * half
        y = top + (0.16 + 0.06 * index) * height
        paths.append(GeometryPath((
            ("M", (x, y)),
            ("C", (x - 0.04 * half, y + 0.10 * height, x + 0.04 * half, y + 0.18 * height, x, y + 0.26 * height)),
        )))
        surfaces.append(GeometrySurface(f"hair_detail:strand_{index}", {
            "path_index": index + 1, "semantic_region": "HAIR_DETAIL", "depth_layer": 1, "component_id": component.id,
        }))
    return GeometryContract(
        coordinate_frame="component",
        bounds=GeometryBounds(cx - 1.02 * half, top - 0.02 * height, cx + 1.02 * half, hairline + 0.42 * height),
        paths=tuple(paths),
        surfaces=tuple(surfaces),
        anchors={"center": (cx, cy, 0.0)},
        local_z=0.0,
    )


def hair_geometry_generator() -> RegisteredGeometryGenerator:
    return RegisteredGeometryGenerator(
        name=HAIR_GEOMETRY_GENERATOR,
        version=HAIR_GEOMETRY_GENERATOR_VERSION,
        kinds=("Hair",),
        generate_fn=generate_hair_geometry,
        cache_inputs_fn=lambda inputs: None,
    )
