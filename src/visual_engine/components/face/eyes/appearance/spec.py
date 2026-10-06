from dataclasses import dataclass, field

from ..contracts.validation import _color, _finite
from ..eyelid.spec import EyelidAppearance
from .contour import ContourSpec
from ..eyebrow.spec import BrowSpec
from .caruncle import CaruncleSpec
from ..highlights.spec import ReflectionMark
from ..iris.spec import IrisSpec
from ..lashes.spec import LashSpec, LowerLashSpec
from ..lashes.effects import LashShadowSpec  # PILOT-IMPACT: consume the lash-owned shadow contract.
from ..pupil.spec import PupilSpec
from ..contracts.types import *
from ..visibility import EyeVisibilitySpec

@dataclass(frozen=True, slots=True)
class EyeAppearance:
    sclera: str = "#ffffff"
    contour: ContourSpec = field(default_factory=ContourSpec)
    eyelid: EyelidAppearance = field(default_factory=EyelidAppearance)
    conjunctiva_color: str = "#ffffff"
    outline: str = "#000000"
    iris: IrisSpec = field(default_factory=IrisSpec)
    pupils: tuple[PupilSpec, ...] = (PupilSpec(),)
    lashes: LashSpec = field(default_factory=LashSpec)
    lash_shadow: LashShadowSpec = field(default_factory=LashShadowSpec)
    lower_lashes: LowerLashSpec = field(default_factory=LowerLashSpec)
    eyebrow: BrowSpec = field(default_factory=BrowSpec)
    # V1.7: medial caruncle is a separate ocular-surface detail, not a canthus bridge.
    caruncle: CaruncleSpec = field(default_factory=CaruncleSpec)
    reflection: str = "#ffffff"
    reflection_opacity: float = 0.9
    reflection_marks: tuple[ReflectionMark, ...] = ()
    sclera_spots: tuple[tuple[float, float, float, str], ...] = ()
    under_eye_marks: tuple[tuple[float, float, float, float, str], ...] = ()
    stress_intensity: float = 0.0
    visibility: EyeVisibilitySpec = field(default_factory=EyeVisibilitySpec)

    def __post_init__(self) -> None:
        if not self.pupils:
            raise ValueError("an eye appearance requires at least one pupil spec")
        if not 0 <= self.reflection_opacity <= 1 or not 0 <= self.stress_intensity <= 1:
            raise ValueError("invalid eye appearance")
        _color(self.sclera, "sclera")
        _color(self.conjunctiva_color, "conjunctiva_color")
        _color(self.outline, "outline")
        _color(self.reflection, "reflection")
        for x, y, radius, color in self.sclera_spots:
            if not _finite((x, y, radius)) or radius <= 0:
                raise ValueError("invalid sclera spot")
            _color(color, "sclera spot color")
        for x, y, length, thickness, color in self.under_eye_marks:
            if not _finite((x, y, length, thickness)) or length < 0 or thickness < 0:
                raise ValueError("invalid under-eye mark")
            _color(color, "under-eye mark color")
