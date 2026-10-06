from __future__ import annotations

"""Explicit HumanFace composite including the production mouth child."""

from dataclasses import dataclass
from typing import Any, Mapping

from visual_engine.components.common.geometry_composition import merge_geometry_contracts
from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.meta import Component
from visual_engine.components.face.generators import (
    FaceWithEyesGeometryInputs,
    _prepare_face_with_eyes,
    _eye_children,
)
from visual_engine.runtime.generators import RegisteredGeometryGenerator
from visual_engine.runtime.versioning import stable_digest

MOUTH_FACE_GENERATOR = "face.human_with_eyes_nose_mouth"
MOUTH_FACE_GENERATOR_VERSION = "1"

@dataclass(frozen=True, slots=True)
class FaceWithEyesNoseMouthGeometryInputs:
    head: GeometryContract | None = None
    eye_pair: GeometryContract | None = None
    nose: GeometryContract | None = None
    mouth: GeometryContract | None = None


def _dependencies(component: Component, inputs: Any = None) -> tuple[str, ...]:
    left, right = _eye_children(component)
    noses = tuple(child for child in component.children if child.kind == "Nose")
    mouths = tuple(child for child in component.children if child.kind == "Mouth")
    if len(noses) != 1 or len(mouths) != 1:
        raise ValueError("face.human_with_eyes_nose_mouth requires exactly one Nose and one Mouth")
    return left.id, right.id, noses[0].id, mouths[0].id


def _prepare(component: Component, inputs: Any, children: Mapping[str, GeometryContract]) -> FaceWithEyesNoseMouthGeometryInputs:
    if inputs is None:
        inputs = FaceWithEyesNoseMouthGeometryInputs()
    if not isinstance(inputs, FaceWithEyesNoseMouthGeometryInputs):
        raise TypeError("face.human_with_eyes_nose_mouth requires prepared inputs")
    base = _prepare_face_with_eyes(component, FaceWithEyesGeometryInputs(), children)
    head, eye_pair = base.head, base.eye_pair
    noses = tuple(child for child in component.children if child.kind == "Nose")
    mouths = tuple(child for child in component.children if child.kind == "Mouth")
    if len(noses) != 1 or len(mouths) != 1 or noses[0].id not in children or mouths[0].id not in children:
        raise ValueError("face.human_with_eyes_nose_mouth child geometry is incomplete")
    return FaceWithEyesNoseMouthGeometryInputs(head, eye_pair, children[noses[0].id], children[mouths[0].id])


def _cache_inputs(inputs: Any) -> Any:
    if not isinstance(inputs, FaceWithEyesNoseMouthGeometryInputs):
        raise TypeError("face.human_with_eyes_nose_mouth requires prepared inputs")
    return {name: stable_digest(value) for name, value in (
        ("head", inputs.head), ("eye_pair", inputs.eye_pair),
        ("nose", inputs.nose), ("mouth", inputs.mouth),
    )}


def generate_face_with_eyes_nose_mouth_geometry(component: Component, inputs: Any = None) -> GeometryContract:
    if not isinstance(inputs, FaceWithEyesNoseMouthGeometryInputs) or any(
        value is None for value in (inputs.head, inputs.eye_pair, inputs.nose, inputs.mouth)
    ):
        raise TypeError("face.human_with_eyes_nose_mouth requires prepared head, eyes, nose and mouth")
    return merge_geometry_contracts(
        {"head": inputs.head, "eyes": inputs.eye_pair, "nose": inputs.nose, "mouth": inputs.mouth},
        coordinate_frame="component",
    )


def face_with_eyes_nose_mouth_geometry_generator() -> RegisteredGeometryGenerator:
    return RegisteredGeometryGenerator(
        name=MOUTH_FACE_GENERATOR,
        version=MOUTH_FACE_GENERATOR_VERSION,
        kinds=("HumanFace",),
        generate_fn=generate_face_with_eyes_nose_mouth_geometry,
        cache_inputs_fn=_cache_inputs,
        geometry_dependencies_fn=_dependencies,
        prepare_inputs_fn=_prepare,
    )
