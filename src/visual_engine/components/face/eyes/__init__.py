"""Face/eye component family.

The eye core owns the coupled geometry contract; subpackages expose stable
domain entry points for pupil, iris, eyelid, lashes, eyebrow and highlights.
"""
from .core import *
from .pair import *
from .profiles import *
from .styles import *
from .expression import *
from .generator import EyeGeometryInputs, EYE_GEOMETRY_GENERATOR, EYE_GEOMETRY_GENERATOR_VERSION, eye_geometry_generator, eye_to_geometry_contract, generate_eye_geometry, default_eye_geometry_registry
