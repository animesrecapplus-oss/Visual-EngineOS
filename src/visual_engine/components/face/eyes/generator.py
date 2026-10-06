from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from visual_engine.components.common.geometry_contract import (
    GeometryBounds, GeometryContract, GeometryPath, GeometryPrimitive, GeometrySurface,
)
from visual_engine.components.common.meta import Component
from .contracts.types import EyeState
from .morphology.spec import EyeParameters
from .appearance.spec import EyeAppearance
from .geometry.types import EyeGeometry
from .gaze.solver import Gaze
from .eyelid.spec import EyelidAppearance
from .iris.spec import IrisSpec
from .pupil.spec import PupilSpec
from .geometry_builder import build_eye_geometry

from visual_engine.runtime.generators import RegisteredGeometryGenerator

EYE_GEOMETRY_GENERATOR = "face.eye"
EYE_GEOMETRY_GENERATOR_VERSION = "10"  # V1.91: HumanFace bilateral side propagation at the Eye input boundary


@dataclass(frozen=True, slots=True)
class EyeGeometryInputs:
    """Explicit generator inputs; visual-only fields are intentionally absent."""

    parameters: EyeParameters = EyeParameters()
    center: tuple[float, float] = (0.0, 0.0)
    state: EyeState = "normal"
    gaze: Gaze = Gaze()
    appearance: EyeAppearance = EyeAppearance()
    expression: str = "neutral"
    side: str = "single"


def _polyline_path(points: tuple[tuple[float, float], ...], *, closed: bool = False) -> GeometryPath:
    if not points:
        return GeometryPath()
    commands: list[tuple[str, tuple[float, ...]]] = [("M", (points[0][0], points[0][1]))]
    commands.extend(("L", (x, y)) for x, y in points[1:])
    if closed:
        commands.append(("Z", ()))
    return GeometryPath(tuple(commands))


def _bounds(points: tuple[tuple[float, float], ...]) -> GeometryBounds:
    if not points:
        return GeometryBounds()
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    return GeometryBounds(min(xs), min(ys), max(xs), max(ys))


def _closed_aperture_path(eye: EyeGeometry) -> GeometryPath:
    """Serialize the geometry-owned lid curves and C1 canthus bridges."""
    upper = eye.upper_lid_points
    lower = tuple(reversed(eye.lower_lid_points))
    if not upper or not lower:
        return GeometryPath()
    commands: list[tuple[str, tuple[float, ...]]] = [("M", upper[0])]
    for x, y in upper[1:]:
        commands.append(("L", (x, y)))
    if len(eye.outer_canthus_bridge) == 4:
        _, c1, c2, end = eye.outer_canthus_bridge
        commands.append(("C", (*c1, *c2, *end)))
    else:
        commands.append(("L", lower[0]))
    for x, y in lower[1:]:
        commands.append(("L", (x, y)))
    if len(eye.inner_canthus_bridge) == 4:
        _, c1, c2, end = eye.inner_canthus_bridge
        commands.append(("C", (*c1, *c2, *end)))
    commands.append(("Z", ()))
    return GeometryPath(tuple(commands))


def eye_to_geometry_contract(
    eye: EyeGeometry,
    *,
    iris_shape: str = "circle",
    pupil_shapes: tuple[str, ...] = (),
) -> GeometryContract:
    """Adapt the existing eye solver output into the renderer-neutral contract.

    The adapter contains geometry only. Color, opacity, lash style and other visual
    choices stay outside this contract so a visual-only change does not rebuild it.
    """
    all_points = tuple(eye.contour_points) + tuple(eye.upper_crease_points) + tuple(eye.lower_crease_points)
    paths = (
        _closed_aperture_path(eye),
        _polyline_path(eye.upper_lid_points),
        _polyline_path(eye.lower_lid_points),
        _polyline_path(eye.upper_crease_points),
        _polyline_path(eye.lower_crease_points),
        _polyline_path(eye.epicanthic_fold_points),
        _polyline_path(eye.medial_caruncle_points, closed=True),
    )
    primitives: list[GeometryPrimitive] = [
        GeometryPrimitive("ellipse", {"role": "iris", "shape": iris_shape, "cx": eye.iris_center[0], "cy": eye.iris_center[1], "rx": eye.iris_rx, "ry": eye.iris_ry, "rotation_deg": eye.iris_rotation_deg}),
        GeometryPrimitive("ellipse", {"role": "reflection", "cx": eye.reflection_center[0], "cy": eye.reflection_center[1], "rx": eye.reflection_rx, "ry": eye.reflection_ry, "rotation_deg": eye.reflection_rotation_deg}),
    ]
    for index, (center, radii) in enumerate(zip(eye.pupil_centers, eye.pupil_radii)):
        shape = pupil_shapes[index] if index < len(pupil_shapes) else "ellipse"
        primitives.append(GeometryPrimitive("ellipse", {
            "role": "pupil", "index": index, "shape": shape, "cx": center[0], "cy": center[1], "rx": radii[0], "ry": radii[1], "rotation_deg": eye.pupil_rotation_degs[index],
        }))
    surfaces = (
        GeometrySurface("aperture", {"path_index": 0}),
        GeometrySurface("upper_lid", {"path_index": 1}),
        GeometrySurface("lower_lid", {"path_index": 2}),
        GeometrySurface("upper_crease", {"path_index": 3}),
        GeometrySurface("lower_crease", {"path_index": 4}),
        GeometrySurface("iris", {"primitive_role": "iris", "projection": "spherical_v1_14" if eye.spherical_assembly else "legacy"}),
        GeometrySurface("pupil", {"primitive_role": "pupil", "projection": "spherical_v1_14" if eye.spherical_assembly else "legacy"}),
        GeometrySurface("eyelid_globe_coupling", {"enabled": eye.spherical_assembly is not None}),
        GeometrySurface("reflection", {"primitive_role": "reflection"}),
        GeometrySurface("epicanthic_fold", {"path_index": 5}),
        GeometrySurface("medial_caruncle", {"path_index": 6}),
    )
    if eye.spherical_assembly is not None:
        sa = eye.spherical_assembly
        surfaces = surfaces + (
            GeometrySurface("sclera_sphere", {"projection": "spherical_v1_13", "radius": sa.radius}),
            GeometrySurface("cornea", {"projection": "spherical_v1_13", "visibility": sa.visibility.cornea}),
            GeometrySurface("near_canthus", {"visibility": sa.visibility.near_canthus}),
            GeometrySurface("far_canthus", {"visibility": sa.visibility.far_canthus}),
            GeometrySurface("orbital_surface", {"enabled": sa.depth_occlusion is not None}),
            GeometrySurface("ocular_depth_order", {"z_order": sa.depth_occlusion.z_order if sa.depth_occlusion else ()}),
            GeometrySurface("alignment_globe_coupling", {"sign": sa.alignment_coupling.sign if sa.alignment_coupling else "alignment_neutral", "aperture_owner": "face", "globe_owner": "eye"}),
        )
    return GeometryContract(
        coordinate_frame="component",
        bounds=_bounds(all_points),
        primitives=tuple(primitives),
        paths=paths,
        surfaces=surfaces,
        anchors={
            "center": (eye.center_x, eye.center_y, 0.0),
            "inner_canthus": (eye.inner_canthus[0], eye.inner_canthus[1], 0.0),
            "outer_canthus": (eye.outer_canthus[0], eye.outer_canthus[1], 0.0),
            "iris_center": (eye.iris_center[0], eye.iris_center[1], 0.0),
            "pupil_center": (eye.pupil_center[0], eye.pupil_center[1], 0.0),
        },
        local_z=0.0,
    )


def _component_default_eye_inputs(component: Component) -> EyeGeometryInputs:
    values = {name: float(parameter.value) for name, parameter in component.parameters.items()}
    parameters = EyeParameters(
        width=values.get("width", 1.0),
        height=values.get("height", 0.55),
        opening=values.get("opening", 1.0),
        iris_ratio=values.get("iris_ratio", 0.52),
        pupil_ratio=values.get("pupil_ratio", 0.38),
        asymmetry=values.get("asymmetry", 0.0),
        rotation_deg=values.get("rotation_deg", component.transform.rotation_deg),
        alignment_axis_rotation_deg=values.get("alignment_axis_rotation_deg", 0.0),
        ocular_yaw_deg=values.get("ocular_yaw_deg", 0.0),
        ocular_pitch_deg=values.get("ocular_pitch_deg", 0.0),
        eyelid_surface_follow_strength=values.get("eyelid_surface_follow_strength", 0.10),
    )
    anchor = component.anchors.get("center")
    center = (anchor.x, anchor.y) if anchor is not None else (component.transform.x, component.transform.y)
    side = "single"
    if component.kind == "Eye" and component.parent_id is not None:
        side = {"left_eye": "image_left", "right_eye": "image_right"}.get(component.id, "single")
    return EyeGeometryInputs(parameters=parameters, center=center, side=side)


def generate_eye_geometry(component: Component, inputs: Any = None) -> GeometryContract:
    if inputs is None:
        inputs = _component_default_eye_inputs(component)
    if not isinstance(inputs, EyeGeometryInputs):
        raise TypeError("face.eye generator inputs must be EyeGeometryInputs")
    eye = build_eye_geometry(
        inputs.parameters,
        center=inputs.center,
        state=inputs.state,
        gaze=inputs.gaze,
        appearance=inputs.appearance,
        expression=inputs.expression,
        side=inputs.side,
    )
    return eye_to_geometry_contract(
        eye,
        iris_shape=inputs.appearance.iris.shape,
        pupil_shapes=tuple(spec.shape for spec in inputs.appearance.pupils),
    )


def _eye_cache_inputs(inputs: Any) -> Any:
    """Project the eye request to fields that can change generated geometry.

    Colors, opacity, lash systems, eyebrow styling, glow and smoke are visual
    concerns and deliberately do not enter the geometry cache key. Pupil placement
    and scale, eyelid crease geometry and iris shape are retained because they can
    alter geometry.
    """
    if inputs is None:
        inputs = EyeGeometryInputs()
    if not isinstance(inputs, EyeGeometryInputs):
        raise TypeError("face.eye generator inputs must be EyeGeometryInputs")
    p = inputs.parameters
    a = inputs.appearance
    pupils = tuple({
        "x": spec.x, "y": spec.y, "scale": spec.scale, "scale_x": spec.scale_x,
        "scale_y": spec.scale_y, "rotation_deg": spec.rotation_deg, "shape": spec.shape,
    } for spec in a.pupils)
    return {
        "parameters": p,
        "center": inputs.center,
        "state": inputs.state,
        "gaze": inputs.gaze,
        "expression": inputs.expression,
        "side": inputs.side,
        "eyelid": {
            "upper_enabled": a.eyelid.upper_enabled, "lower_enabled": a.eyelid.lower_enabled,
            "upper_crease_enabled": a.eyelid.upper_crease_enabled, "lower_crease_enabled": a.eyelid.lower_crease_enabled,
            "upper_crease_offset": a.eyelid.upper_crease_offset, "lower_crease_offset": a.eyelid.lower_crease_offset,
            "upper_crease_length": a.eyelid.upper_crease_length, "lower_crease_length": a.eyelid.lower_crease_length,
        },
        "iris_shape": a.iris.shape,
        "caruncle_geometry": (a.caruncle.enabled, a.caruncle.width, a.caruncle.height, a.caruncle.curvature),
        "pupils": pupils,
    }


def eye_geometry_generator(*, kinds: tuple[str, ...] = ("eye",)) -> RegisteredGeometryGenerator:
    return RegisteredGeometryGenerator(
        name=EYE_GEOMETRY_GENERATOR,
        version=EYE_GEOMETRY_GENERATOR_VERSION,
        kinds=kinds,
        generate_fn=generate_eye_geometry,
        cache_inputs_fn=_eye_cache_inputs,
        default_inputs_fn=_component_default_eye_inputs,
    )


def default_eye_geometry_registry():
    """Create a registry containing the canonical eye generator."""
    from visual_engine.runtime.generators import GeometryGeneratorRegistry
    registry = GeometryGeneratorRegistry()
    registry.register(eye_geometry_generator())
    return registry
