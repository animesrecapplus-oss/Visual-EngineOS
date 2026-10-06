"""Compatibility facade for the historical ocular definitions module.

Domain ownership lives in focused submodules. This file intentionally contains
no implementation so legacy imports remain stable without creating a new
fourre-tout module.
"""
from .contracts.types import *
from .contracts.validation import _finite, _color
from .morphology.spec import EyeParameters, CanthusTerminalSpec
from .morphology.canthus_profile import CanthusEndpointTangentProfile
from .pupil.effects import PupilGlowSpec, PupilSmokeSpec
from .pupil.spec import PupilSpec
from .iris.spec import IrisSpec
from .eyelid.spec import EyelidAppearance
from .lashes.spec import LashSpec, LowerLashSpec
from .lashes.effects import LashShadowSpec  # PILOT-IMPACT: preserve legacy export through the new owner.
from .eyebrow.spec import BrowSpec
from .highlights.spec import ReflectionMark
from .appearance.spec import EyeAppearance
from .appearance.caruncle import CaruncleSpec
from .visibility import EyeVisibilitySpec, PARENT as EYE_VISIBILITY_PARENT
from .appearance.contour import ContourSpec
from .gaze.solver import (
    GazeSolution, Gaze, BinocularGazeSolution, BinocularGazeSolver, GazeSolver,
)
from .geometry.types import Coverage, EyeGeometry
