from __future__ import annotations

"""Explicit HumanFace production composite including the two ear children."""

from dataclasses import dataclass
from typing import Any, Mapping

from visual_engine.components.common.geometry_composition import merge_geometry_contracts
from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.meta import Component
from visual_engine.components.face.mouth_composite import (
    FaceWithEyesNoseMouthGeometryInputs,
    _cache_inputs as _mouth_cache_inputs,
    _prepare as _prepare_mouth,
    _dependencies as _mouth_dependencies,
    generate_face_with_eyes_nose_mouth_geometry,
)
from visual_engine.runtime.generators import RegisteredGeometryGenerator
from visual_engine.runtime.versioning import stable_digest

EAR_FACE_GENERATOR = "face.human_with_eyes_nose_mouth_ears"
EAR_FACE_GENERATOR_VERSION = "1"


@dataclass(frozen=True, slots=True)
class FaceWithEyesNoseMouthEarsGeometryInputs:
    base: FaceWithEyesNoseMouthGeometryInputs | None = None
    left_ear: GeometryContract | None = None
    right_ear: GeometryContract | None = None


def _ears(component: Component) -> tuple[Component, Component]:
    ears = tuple(sorted((child for child in component.children if child.kind == "Ear"), key=lambda child: child.id))
    if len(ears) != 2:
        raise ValueError(f"{EAR_FACE_GENERATOR} requires exactly two direct Ear children; got {len(ears)}")
    return ears[0], ears[1]


def _dependencies(component: Component, inputs: Any = None) -> tuple[str, ...]:
    left, right = _ears(component)
    return (*_mouth_dependencies(component, inputs), left.id, right.id)


def _prepare(component: Component, inputs: Any, children: Mapping[str, GeometryContract]) -> FaceWithEyesNoseMouthEarsGeometryInputs:
    if inputs is not None and not isinstance(inputs, FaceWithEyesNoseMouthEarsGeometryInputs):
        raise TypeError(f"{EAR_FACE_GENERATOR} requires prepared inputs")
    base = _prepare_mouth(component, FaceWithEyesNoseMouthGeometryInputs(), children)
    left, right = _ears(component)
    if left.id not in children or right.id not in children:
        raise ValueError(f"{EAR_FACE_GENERATOR} ear geometry is incomplete")
    return FaceWithEyesNoseMouthEarsGeometryInputs(base, children[left.id], children[right.id])


def _cache_inputs(inputs: Any) -> Any:
    if not isinstance(inputs, FaceWithEyesNoseMouthEarsGeometryInputs):
        raise TypeError(f"{EAR_FACE_GENERATOR} requires prepared inputs")
    return {
        "base": _mouth_cache_inputs(inputs.base),
        "left_ear": stable_digest(inputs.left_ear),
        "right_ear": stable_digest(inputs.right_ear),
    }


def generate_face_with_eyes_nose_mouth_ears_geometry(component: Component, inputs: Any = None) -> GeometryContract:
    if not isinstance(inputs, FaceWithEyesNoseMouthEarsGeometryInputs) or inputs.base is None:
        raise TypeError(f"{EAR_FACE_GENERATOR} requires prepared base and ear geometry")
    if inputs.left_ear is None or inputs.right_ear is None:
        raise TypeError(f"{EAR_FACE_GENERATOR} requires both ear geometries")
    base = generate_face_with_eyes_nose_mouth_geometry(component, inputs.base)
    # Ear uses the generic depth contract plus an explicit renderer role priority;
    # no negative depth semantics are introduced by this composite.
    return merge_geometry_contracts(
        {"left_ear": inputs.left_ear, "right_ear": inputs.right_ear, "face": base},
        coordinate_frame="component",
    )


def face_with_eyes_nose_mouth_ears_geometry_generator() -> RegisteredGeometryGenerator:
    return RegisteredGeometryGenerator(
        name=EAR_FACE_GENERATOR,
        version=EAR_FACE_GENERATOR_VERSION,
        kinds=("HumanFace",),
        generate_fn=generate_face_with_eyes_nose_mouth_ears_geometry,
        cache_inputs_fn=_cache_inputs,
        geometry_dependencies_fn=_dependencies,
        prepare_inputs_fn=_prepare,
    )
