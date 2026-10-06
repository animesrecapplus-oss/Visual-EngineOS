from __future__ import annotations

"""Renderer-neutral production geometry for the HumanFace mouth component."""

import math

from visual_engine.components.common.geometry_contract import GeometryBounds, GeometryContract, GeometryPrimitive, GeometrySurface
from visual_engine.components.common.meta import Component
from visual_engine.runtime.generators import RegisteredGeometryGenerator

MOUTH_GEOMETRY_GENERATOR = "face.mouth"
MOUTH_GEOMETRY_GENERATOR_VERSION = "1"


def _value(component: Component, name: str, default: float) -> float:
    parameter = component.parameters.get(name)
    if parameter is None:
        return default
    value = parameter.value
    # Parameter normally enforces this; keep the geometry owner defensive when
    # malformed Component state bypasses that construction boundary.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"mouth {name} must be numeric")
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"mouth {name} must be finite")
    return value


def generate_mouth_geometry(component: Component, inputs=None) -> GeometryContract:
    """Generate one finite, filled mouth aperture in the component-local frame."""
    if inputs is not None:
        raise TypeError("face.mouth generator does not accept custom inputs")
    width = _value(component, "width", 0.28)
    height = _value(component, "height", 0.08)
    anchor = component.anchors.get("center")
    cx = 0.0 if anchor is None else float(anchor.x)
    cy = 0.28 if anchor is None else float(anchor.y)
    if width <= 0.0 or height <= 0.0:
        raise ValueError("mouth width and height must be positive")
    rx, ry = 0.5 * width, 0.5 * height
    # Positive subnormal dimensions can round to a zero radius; that would
    # violate the leaf contract despite the authored value being positive.
    if rx <= 0.0 or ry <= 0.0:
        raise ValueError("mouth dimensions are below representable geometry precision")
    return GeometryContract(
        coordinate_frame="component",
        bounds=GeometryBounds(cx - rx, cy - ry, cx + rx, cy + ry),
        primitives=(GeometryPrimitive("ellipse", {
            "cx": cx, "cy": cy, "rx": rx, "ry": ry,
            "rotation_deg": 0.0, "role": "mouth", "semantic_region": "MOUTH",
            "component_id": component.id,
        }),),
        surfaces=(GeometrySurface("mouth", {
            "semantic_region": "MOUTH", "depth_layer": 1,
            "component_id": component.id,
        }),),
        anchors={"center": (cx, cy, 0.0)},
    )


def mouth_geometry_generator() -> RegisteredGeometryGenerator:
    return RegisteredGeometryGenerator(
        name=MOUTH_GEOMETRY_GENERATOR,
        version=MOUTH_GEOMETRY_GENERATOR_VERSION,
        kinds=("Mouth",),
        generate_fn=generate_mouth_geometry,
        cache_inputs_fn=lambda inputs: None,
    )
