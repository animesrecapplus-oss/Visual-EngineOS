from __future__ import annotations

"""Renderer-neutral production geometry for one HumanFace ear child."""

import math

from visual_engine.components.common.geometry_contract import GeometryBounds, GeometryContract, GeometryPath, GeometrySurface
from visual_engine.components.common.meta import Component
from visual_engine.runtime.generators import RegisteredGeometryGenerator

EAR_GEOMETRY_GENERATOR = "face.ear"
EAR_GEOMETRY_GENERATOR_VERSION = "1"


def _value(component: Component, name: str, default: float) -> float:
    parameter = component.parameters.get(name)
    if parameter is None:
        return default
    value = parameter.value
    # The generic Parameter contract rejects non-finite numeric values, but
    # malformed Component instances can bypass that constructor boundary.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"ear {name} must be numeric")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"ear {name} must be finite")
    return value


def generate_ear_geometry(component: Component, inputs=None) -> GeometryContract:
    """Generate one finite closed ear silhouette in the component-local frame."""
    if inputs is not None:
        raise TypeError("face.ear generator does not accept custom inputs")
    width = _value(component, "width", 0.20)
    height = _value(component, "height", 0.34)
    anchor = component.anchors.get("center")
    cx = 0.0 if anchor is None else float(anchor.x)
    cy = 0.0 if anchor is None else float(anchor.y)
    if width <= 0.0 or height <= 0.0:
        raise ValueError("ear width and height must be positive")
    rx, ry = 0.5 * width, 0.5 * height
    # Reject positive subnormal dimensions that collapse to a zero-radius path.
    if rx <= 0.0 or ry <= 0.0:
        raise ValueError("ear dimensions are below representable geometry precision")
    commands = (
        ("M", (cx, cy - ry)),
        ("C", (cx - 0.92 * rx, cy - 0.90 * ry, cx - 1.02 * rx, cy + 0.05 * ry, cx - 0.46 * rx, cy + 0.78 * ry)),
        ("C", (cx - 0.18 * rx, cy + 1.02 * ry, cx + 0.48 * rx, cy + 0.90 * ry, cx + 0.70 * rx, cy + 0.35 * ry)),
        ("C", (cx + 0.86 * rx, cy - 0.10 * ry, cx + 0.52 * rx, cy - 0.78 * ry, cx, cy - ry)),
        ("Z", ()),
    )
    return GeometryContract(
        coordinate_frame="component",
        bounds=GeometryBounds(cx - rx, cy - ry, cx + rx, cy + ry),
        paths=(GeometryPath(commands),),
        surfaces=(GeometrySurface("ear", {
            "path_index": 0, "semantic_region": "EAR", "depth_layer": 0, "component_id": component.id,
        }),),
        anchors={"center": (cx, cy, 0.0)},
        local_z=0.0,
    )


def ear_geometry_generator() -> RegisteredGeometryGenerator:
    return RegisteredGeometryGenerator(
        name=EAR_GEOMETRY_GENERATOR,
        version=EAR_GEOMETRY_GENERATOR_VERSION,
        kinds=("Ear",),
        generate_fn=generate_ear_geometry,
        cache_inputs_fn=lambda inputs: None,
    )
