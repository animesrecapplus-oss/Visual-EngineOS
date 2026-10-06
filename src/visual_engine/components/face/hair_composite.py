from __future__ import annotations

"""Explicit HumanFace production composite including one Hair child."""

from dataclasses import dataclass
from typing import Any, Mapping

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.geometry_composition import merge_geometry_contracts
from visual_engine.components.common.meta import Component
from visual_engine.components.face.ear_composite import (
    FaceWithEyesNoseMouthEarsGeometryInputs,
    _cache_inputs as _ear_cache_inputs,
    _prepare as _prepare_ears,
    _dependencies as _ear_dependencies,
    generate_face_with_eyes_nose_mouth_ears_geometry,
)
from visual_engine.runtime.generators import RegisteredGeometryGenerator
from visual_engine.runtime.versioning import stable_digest

HAIR_FACE_GENERATOR = "face.human_with_eyes_nose_mouth_ears_hair"
HAIR_FACE_GENERATOR_VERSION = "1"


@dataclass(frozen=True, slots=True)
class FaceWithEyesNoseMouthEarsHairGeometryInputs:
    base: FaceWithEyesNoseMouthEarsGeometryInputs | None = None
    hair: GeometryContract | None = None


def _hair(component: Component) -> Component:
    hairs = tuple(child for child in component.children if child.kind == "Hair")
    if len(hairs) != 1:
        raise ValueError(f"{HAIR_FACE_GENERATOR} requires exactly one direct Hair child; got {len(hairs)}")
    return hairs[0]


def _dependencies(component: Component, inputs: Any = None) -> tuple[str, ...]:
    return (*_ear_dependencies(component, inputs), _hair(component).id)


def _prepare(component: Component, inputs: Any, children: Mapping[str, GeometryContract]) -> FaceWithEyesNoseMouthEarsHairGeometryInputs:
    if inputs is not None and not isinstance(inputs, FaceWithEyesNoseMouthEarsHairGeometryInputs):
        raise TypeError(f"{HAIR_FACE_GENERATOR} requires prepared inputs")
    base = _prepare_ears(component, None, children)
    hair = _hair(component)
    if hair.id not in children:
        raise ValueError(f"{HAIR_FACE_GENERATOR} hair geometry is incomplete")
    return FaceWithEyesNoseMouthEarsHairGeometryInputs(base, children[hair.id])


def _cache_inputs(inputs: Any) -> Any:
    if not isinstance(inputs, FaceWithEyesNoseMouthEarsHairGeometryInputs) or inputs.base is None or inputs.hair is None:
        raise TypeError(f"{HAIR_FACE_GENERATOR} requires prepared base and hair geometry")
    return {"base": _ear_cache_inputs(inputs.base), "hair": stable_digest(inputs.hair)}


def generate_face_with_eyes_nose_mouth_ears_hair_geometry(component: Component, inputs: Any = None) -> GeometryContract:
    if not isinstance(inputs, FaceWithEyesNoseMouthEarsHairGeometryInputs) or inputs.base is None or inputs.hair is None:
        raise TypeError(f"{HAIR_FACE_GENERATOR} requires prepared base and hair geometry")
    base = generate_face_with_eyes_nose_mouth_ears_geometry(component, inputs.base)
    return merge_geometry_contracts({"hair": inputs.hair, "face": base}, coordinate_frame="component")


def face_with_eyes_nose_mouth_ears_hair_geometry_generator() -> RegisteredGeometryGenerator:
    return RegisteredGeometryGenerator(
        name=HAIR_FACE_GENERATOR,
        version=HAIR_FACE_GENERATOR_VERSION,
        kinds=("HumanFace",),
        generate_fn=generate_face_with_eyes_nose_mouth_ears_hair_geometry,
        cache_inputs_fn=_cache_inputs,
        geometry_dependencies_fn=_dependencies,
        prepare_inputs_fn=_prepare,
    )
