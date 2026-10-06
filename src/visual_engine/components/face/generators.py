from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

from visual_engine.components.common.geometry_composition import merge_geometry_contracts
from visual_engine.components.common.geometry_contract import GeometryBounds, GeometryContract, GeometryPath, GeometryPrimitive, GeometrySurface
from visual_engine.components.common.meta import Component
from visual_engine.components.face.eyes.core import EyeAppearance, EyeParameters, Gaze, build_eye_geometry
from visual_engine.components.face.eyes.generator import EyeGeometryInputs, eye_to_geometry_contract
from visual_engine.runtime.generators import RegisteredGeometryGenerator
from visual_engine.runtime.versioning import stable_digest

FACE_GEOMETRY_GENERATOR = "face.human"
FACE_GEOMETRY_GENERATOR_VERSION = "1"
EYE_PAIR_GEOMETRY_GENERATOR = "face.eye_pair"
EYE_PAIR_GEOMETRY_GENERATOR_VERSION = "1"
FACE_WITH_EYES_GEOMETRY_GENERATOR = "face.human_with_eyes"
FACE_WITH_EYES_GEOMETRY_GENERATOR_VERSION = "1"
FACE_WITH_EYES_NOSE_GEOMETRY_GENERATOR = "face.human_with_eyes_nose"
FACE_WITH_EYES_NOSE_GEOMETRY_GENERATOR_VERSION = "1"
NOSE_GEOMETRY_GENERATOR = "face.nose"
NOSE_GEOMETRY_GENERATOR_VERSION = "1"


@dataclass(frozen=True, slots=True)
class FaceGeometryInputs:
    head_scale_x: float = 1.0
    head_scale_y: float = 1.2


@dataclass(frozen=True, slots=True)
class EyePairGeometryInputs:
    child_geometries: Mapping[str, GeometryContract] = field(default_factory=dict)

    def __post_init__(self) -> None:
        object.__setattr__(self, "child_geometries", dict(self.child_geometries or {}))


@dataclass(frozen=True, slots=True)
class FaceWithEyesGeometryInputs:
    head: GeometryContract | None = None
    eye_pair: GeometryContract | None = None


@dataclass(frozen=True, slots=True)
class FaceWithEyesNoseGeometryInputs:
    head: GeometryContract | None = None
    eye_pair: GeometryContract | None = None
    nose: GeometryContract | None = None


def _parameter(component: Component, name: str, default: float) -> float:
    parameter = component.parameters.get(name)
    return default if parameter is None else float(parameter.value)


def _head_geometry(component: Component, inputs: FaceGeometryInputs) -> GeometryContract:
    width = _parameter(component, "width", 1.0) * inputs.head_scale_x
    height = _parameter(component, "height", 1.2) * inputs.head_scale_y
    # Parametric closed oval. The contour is geometry; fill/line styling remains
    # a renderer concern.
    samples = 64
    import math
    points = tuple((0.5 * width * math.cos(2 * math.pi * i / samples), 0.5 * height * math.sin(2 * math.pi * i / samples)) for i in range(samples))
    commands = (("M", points[0]),) + tuple(("L", p) for p in points[1:]) + (("Z", ()),)
    return GeometryContract(
        coordinate_frame="component",
        bounds=GeometryBounds(-0.5 * width, -0.5 * height, 0.5 * width, 0.5 * height),
        paths=(GeometryPath(commands),),
        surfaces=(GeometrySurface("head", {"path_index": 0, "semantic_region": "HEAD", "depth_layer": 0}),),
        anchors={
            "center": (0.0, 0.0, 0.0),
            "forehead": (0.0, -0.25 * height, 0.0),
            "chin": (0.0, 0.5 * height, 0.0),
            "left_eye_region": (-0.28 * width, -0.05 * height, 0.0),
            "right_eye_region": (0.28 * width, -0.05 * height, 0.0),
        },
    )


def _face_cache_inputs(inputs: Any) -> Any:
    if inputs is None:
        return FaceGeometryInputs()
    if not isinstance(inputs, FaceGeometryInputs):
        raise TypeError("face.human generator inputs must be FaceGeometryInputs")
    return inputs


def generate_face_geometry(component: Component, inputs: Any = None) -> GeometryContract:
    inputs = inputs if inputs is not None else FaceGeometryInputs()
    if not isinstance(inputs, FaceGeometryInputs):
        raise TypeError("face.human generator inputs must be FaceGeometryInputs")
    return _head_geometry(component, inputs)


def face_geometry_generator() -> RegisteredGeometryGenerator:
    return RegisteredGeometryGenerator(
        name=FACE_GEOMETRY_GENERATOR,
        version=FACE_GEOMETRY_GENERATOR_VERSION,
        kinds=("HumanFace",),
        generate_fn=generate_face_geometry,
        cache_inputs_fn=_face_cache_inputs,
    )


def _eye_children(component: Component) -> tuple[Component, Component]:
    eyes = tuple(sorted((child for child in component.children if child.kind == "Eye"), key=lambda child: child.id))
    if len(eyes) != 2:
        raise ValueError(f"face.eye_pair requires exactly two direct Eye children; got {len(eyes)}")
    return eyes[0], eyes[1]


def _eye_pair_dependencies(component: Component, inputs: Any = None) -> tuple[str, ...]:
    left, right = _eye_children(component)
    return left.id, right.id


def _eye_pair_cache_inputs(inputs: Any) -> Any:
    if inputs is None:
        return EyePairGeometryInputs()
    if not isinstance(inputs, EyePairGeometryInputs):
        raise TypeError("face.eye_pair generator inputs must be EyePairGeometryInputs")
    return {"children": tuple((key, stable_digest(value)) for key, value in sorted(inputs.child_geometries.items()))}


def _prepare_eye_pair(component: Component, inputs: Any, children: Mapping[str, GeometryContract]) -> EyePairGeometryInputs:
    if inputs is None:
        inputs = EyePairGeometryInputs()
    if not isinstance(inputs, EyePairGeometryInputs):
        raise TypeError("face.eye_pair generator inputs must be EyePairGeometryInputs")
    return EyePairGeometryInputs(child_geometries=children)


def generate_eye_pair_geometry(component: Component, inputs: Any = None) -> GeometryContract:
    if not isinstance(inputs, EyePairGeometryInputs):
        raise TypeError("face.eye_pair generator requires prepared EyePairGeometryInputs")
    expected = {child.id for child in component.children if child.kind == "Eye"}
    if set(inputs.child_geometries) != expected:
        raise ValueError("face.eye_pair child geometry set does not match direct Eye children")
    return merge_geometry_contracts(inputs.child_geometries, coordinate_frame="component")


def eye_pair_geometry_generator() -> RegisteredGeometryGenerator:
    return RegisteredGeometryGenerator(
        name=EYE_PAIR_GEOMETRY_GENERATOR,
        version=EYE_PAIR_GEOMETRY_GENERATOR_VERSION,
        kinds=("HumanFace",),
        generate_fn=generate_eye_pair_geometry,
        cache_inputs_fn=_eye_pair_cache_inputs,
        geometry_dependencies_fn=_eye_pair_dependencies,
        prepare_inputs_fn=_prepare_eye_pair,
    )


def _face_with_eyes_dependencies(component: Component, inputs: Any = None) -> tuple[str, ...]:
    left, right = _eye_children(component)
    return left.id, right.id


def _face_with_eyes_cache_inputs(inputs: Any) -> Any:
    if inputs is None:
        return FaceWithEyesGeometryInputs()
    if not isinstance(inputs, FaceWithEyesGeometryInputs):
        raise TypeError("face.human_with_eyes generator inputs must be FaceWithEyesGeometryInputs")
    return {
        "head": stable_digest(inputs.head) if inputs.head is not None else None,
        "eye_pair": stable_digest(inputs.eye_pair) if inputs.eye_pair is not None else None,
    }


def _prepare_face_with_eyes(component: Component, inputs: Any, children: Mapping[str, GeometryContract]) -> FaceWithEyesGeometryInputs:
    if inputs is None:
        inputs = FaceWithEyesGeometryInputs()
    if not isinstance(inputs, FaceWithEyesGeometryInputs):
        raise TypeError("face.human_with_eyes generator inputs must be FaceWithEyesGeometryInputs")
    # Head and eye pair are generated from the same component in this explicit
    # composite boundary. Child geometry is the only external geometry dependency.
    # Stamp the actual owner into the head surface metadata before composition; the
    # generic renderer must not have to guess that the synthetic "head" slot is
    # actually owned by the requested face component.
    head_geometry = _head_geometry(component, FaceGeometryInputs())
    head = GeometryContract(
        coordinate_frame=head_geometry.coordinate_frame,
        bounds=head_geometry.bounds,
        primitives=head_geometry.primitives,
        paths=head_geometry.paths,
        surfaces=tuple(
            GeometrySurface(surface.name, {**surface.data, "component_id": component.id})
            for surface in head_geometry.surfaces
        ),
        masks=head_geometry.masks,
        anchors=head_geometry.anchors,
        local_z=head_geometry.local_z,
    )
    eye_children = {child.id: children[child.id] for child in _eye_children(component)}
    eye_pair = merge_geometry_contracts(eye_children, coordinate_frame="component")
    return FaceWithEyesGeometryInputs(head=head, eye_pair=eye_pair)


def generate_face_with_eyes_geometry(component: Component, inputs: Any = None) -> GeometryContract:
    if not isinstance(inputs, FaceWithEyesGeometryInputs) or inputs.head is None or inputs.eye_pair is None:
        raise TypeError("face.human_with_eyes generator requires prepared head and eye-pair geometry")
    return merge_geometry_contracts({"head": inputs.head, "eyes": inputs.eye_pair}, coordinate_frame="component")


def face_with_eyes_geometry_generator() -> RegisteredGeometryGenerator:
    return RegisteredGeometryGenerator(
        name=FACE_WITH_EYES_GEOMETRY_GENERATOR,
        version=FACE_WITH_EYES_GEOMETRY_GENERATOR_VERSION,
        kinds=("HumanFace",),
        generate_fn=generate_face_with_eyes_geometry,
        cache_inputs_fn=_face_with_eyes_cache_inputs,
        geometry_dependencies_fn=_face_with_eyes_dependencies,
        prepare_inputs_fn=_prepare_face_with_eyes,
    )


def _nose_geometry(component: Component) -> GeometryContract:
    """Build a restrained stylized nose in the existing face-local frame.

    V1.46 deliberately avoids pretending to solve full nasal morphology. The
    production contract is a readable silhouette with a rounded bridge/tip and
    two shallow nostril curves; shading, pores and material effects remain out of
    scope until a real consumer requires them.
    """
    width = _parameter(component, "width", 0.12)
    height = _parameter(component, "height", 0.30)
    if width <= 0 or height <= 0:
        raise ValueError("nose width and height must be positive")

    half = 0.5 * width
    # Keep the bridge below the default eye-center line; this is an aesthetic
    # face proportion, not a universal anatomical constraint.
    top = 0.02 * height
    bridge = 0.42 * height
    tip = 0.86 * height
    side = 0.76 * half
    commands = (
        ("M", (-0.22 * half, top)),
        ("C", (-0.16 * half, 0.04 * height, -0.18 * half, 0.20 * height, -0.34 * half, bridge)),
        ("C", (-0.42 * half, 0.54 * height, -0.82 * half, 0.68 * height, -side, 0.76 * height)),
        ("C", (-0.92 * half, 0.82 * height, -0.80 * half, tip, -0.46 * half, 0.98 * height)),
        ("C", (-0.26 * half, 1.00 * height, -0.12 * half, 0.92 * height, 0.0, 0.93 * height)),
        ("C", (0.12 * half, 0.92 * height, 0.26 * half, 1.00 * height, 0.46 * half, 0.98 * height)),
        ("C", (0.80 * half, tip, 0.92 * half, 0.82 * height, side, 0.76 * height)),
        ("C", (0.82 * half, 0.68 * height, 0.42 * half, 0.54 * height, 0.34 * half, bridge)),
        ("C", (0.18 * half, 0.20 * height, 0.16 * half, 0.04 * height, 0.22 * half, top)),
        ("C", (0.10 * half, -0.22 * height, -0.10 * half, -0.22 * height, -0.22 * half, top)),
        ("Z", ()),
    )

    # These are intentionally open strokes: they communicate nostril placement
    # without introducing a boolean/mask dependency into the first nose slice.
    nostril_y = 0.78 * height
    nostril_half_width = 0.15 * half
    nostril_drop = 0.045 * height
    nostrils = (
        GeometryPath((
            ("M", (-0.47 * half, nostril_y)),
            ("C", (-0.40 * half, nostril_y + nostril_drop, -0.25 * half, nostril_y + nostril_drop, -0.18 * half, nostril_y)),
        )),
        GeometryPath((
            ("M", (0.18 * half, nostril_y)),
            ("C", (0.25 * half, nostril_y + nostril_drop, 0.40 * half, nostril_y + nostril_drop, 0.47 * half, nostril_y)),
        )),
    )
    return GeometryContract(
        coordinate_frame="component",
        bounds=GeometryBounds(-0.92 * half, top, 0.92 * half, tip),
        paths=(GeometryPath(commands), *nostrils),
        surfaces=(
            GeometrySurface("nose", {"path_index": 0, "semantic_region": "NOSE", "depth_layer": 1}),
            GeometrySurface("nose_detail:left_nostril", {"path_index": 1, "semantic_region": "NOSE_DETAIL", "depth_layer": 1}),
            GeometrySurface("nose_detail:right_nostril", {"path_index": 2, "semantic_region": "NOSE_DETAIL", "depth_layer": 1}),
        ),
        anchors={"center": (0.0, 0.0, 0.0), "tip": (0.0, tip, 0.0)},
    )


def generate_nose_geometry(component: Component, inputs: Any = None) -> GeometryContract:
    if inputs is not None:
        raise TypeError("face.nose generator does not accept custom inputs yet")
    return _nose_geometry(component)


def nose_geometry_generator() -> RegisteredGeometryGenerator:
    return RegisteredGeometryGenerator(
        name=NOSE_GEOMETRY_GENERATOR,
        version=NOSE_GEOMETRY_GENERATOR_VERSION,
        kinds=("Nose",),
        generate_fn=generate_nose_geometry,
        cache_inputs_fn=lambda inputs: None,
    )


def _face_with_eyes_nose_dependencies(component: Component, inputs: Any = None) -> tuple[str, ...]:
    left, right = _eye_children(component)
    noses = tuple(child for child in component.children if child.kind == "Nose")
    if len(noses) != 1:
        raise ValueError(f"face.human_with_eyes_nose requires exactly one direct Nose child; got {len(noses)}")
    return left.id, right.id, noses[0].id


def _face_with_eyes_nose_cache_inputs(inputs: Any) -> Any:
    if inputs is None:
        return FaceWithEyesNoseGeometryInputs()
    if not isinstance(inputs, FaceWithEyesNoseGeometryInputs):
        raise TypeError("face.human_with_eyes_nose generator inputs must be FaceWithEyesNoseGeometryInputs")
    return {
        "head": stable_digest(inputs.head) if inputs.head is not None else None,
        "eye_pair": stable_digest(inputs.eye_pair) if inputs.eye_pair is not None else None,
        "nose": stable_digest(inputs.nose) if inputs.nose is not None else None,
    }


def _prepare_face_with_eyes_nose(component: Component, inputs: Any, children: Mapping[str, GeometryContract]) -> FaceWithEyesNoseGeometryInputs:
    if inputs is None:
        inputs = FaceWithEyesNoseGeometryInputs()
    if not isinstance(inputs, FaceWithEyesNoseGeometryInputs):
        raise TypeError("face.human_with_eyes_nose generator requires FaceWithEyesNoseGeometryInputs")
    base = _prepare_face_with_eyes(component, FaceWithEyesGeometryInputs(), children)
    noses = tuple(child for child in component.children if child.kind == "Nose")
    if len(noses) != 1 or noses[0].id not in children:
        raise ValueError("face.human_with_eyes_nose nose dependency is missing")
    return FaceWithEyesNoseGeometryInputs(head=base.head, eye_pair=base.eye_pair, nose=children[noses[0].id])


def generate_face_with_eyes_nose_geometry(component: Component, inputs: Any = None) -> GeometryContract:
    if not isinstance(inputs, FaceWithEyesNoseGeometryInputs) or inputs.head is None or inputs.eye_pair is None or inputs.nose is None:
        raise TypeError("face.human_with_eyes_nose generator requires prepared head, eye-pair and nose geometry")
    return merge_geometry_contracts(
        {"head": inputs.head, "eyes": inputs.eye_pair, "nose": inputs.nose},
        coordinate_frame="component",
    )


def face_with_eyes_nose_geometry_generator() -> RegisteredGeometryGenerator:
    return RegisteredGeometryGenerator(
        name=FACE_WITH_EYES_NOSE_GEOMETRY_GENERATOR,
        version=FACE_WITH_EYES_NOSE_GEOMETRY_GENERATOR_VERSION,
        kinds=("HumanFace",),
        generate_fn=generate_face_with_eyes_nose_geometry,
        cache_inputs_fn=_face_with_eyes_nose_cache_inputs,
        geometry_dependencies_fn=_face_with_eyes_nose_dependencies,
        prepare_inputs_fn=_prepare_face_with_eyes_nose,
    )


def default_face_geometry_registry():
    from visual_engine.runtime.generators import GeometryGeneratorRegistry
    from visual_engine.components.face.eyes.generator import eye_geometry_generator
    registry = GeometryGeneratorRegistry()
    registry.register(face_geometry_generator())
    registry.register(eye_geometry_generator(kinds=("eye", "Eye")))
    # Explicit alternatives for the same semantic component kind are legal only
    # when selected by name. The registry's default remains face.human.
    registry.register(eye_pair_geometry_generator(), default=False)
    registry.register(face_with_eyes_geometry_generator(), default=False)
    registry.register(nose_geometry_generator())
    registry.register(face_with_eyes_nose_geometry_generator(), default=False)
    return registry
