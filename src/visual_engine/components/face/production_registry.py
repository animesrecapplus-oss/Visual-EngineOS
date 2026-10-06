from __future__ import annotations

"""Production-only extension of the stable face geometry registry."""

from visual_engine.components.face.generators import default_face_geometry_registry
from visual_engine.components.face.mouth import mouth_geometry_generator
from visual_engine.components.face.mouth_composite import face_with_eyes_nose_mouth_geometry_generator
from visual_engine.components.face.ear import ear_geometry_generator
from visual_engine.components.face.ear_composite import face_with_eyes_nose_mouth_ears_geometry_generator
from visual_engine.components.face.hair import hair_geometry_generator
from visual_engine.components.face.hair_composite import face_with_eyes_nose_mouth_ears_hair_geometry_generator


def production_face_geometry_registry():
    """Return the existing registry plus the certified Mouth, Ear and Hair families."""
    registry = default_face_geometry_registry()
    registry.register(mouth_geometry_generator())
    registry.register(face_with_eyes_nose_mouth_geometry_generator(), default=False)
    registry.register(ear_geometry_generator())
    registry.register(face_with_eyes_nose_mouth_ears_geometry_generator(), default=False)
    registry.register(hair_geometry_generator())
    registry.register(face_with_eyes_nose_mouth_ears_hair_geometry_generator(), default=False)
    return registry
