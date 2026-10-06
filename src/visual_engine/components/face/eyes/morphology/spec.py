from dataclasses import dataclass
from typing import Literal
import math

from ..contracts.types import EyeShape
from ..contracts.validation import _finite
from .canthus_profile import CanthusEndpointTangentProfile


@dataclass(frozen=True, slots=True)
class CanthusTerminalSpec:
    """Terminal topology for one ocular corner.

    ``shared_point`` is the V1.7 visual default: upper and lower lid margins
    converge to the same semantic terminal and no artificial cubic closure stroke
    is emitted. ``bridge`` retains the earlier finite-gap representation for
    explicitly authored morphology experiments and regression tests.
    """

    mode: Literal["shared_point", "bridge"] = "shared_point"

    def __post_init__(self) -> None:
        if self.mode not in {"shared_point", "bridge"}:
            raise ValueError("unknown canthus terminal mode")


@dataclass(frozen=True, slots=True)
class EyeParameters:
    width: float = 1.0
    height: float = 0.55
    opening: float = 1.0
    iris_ratio: float = 0.52
    pupil_ratio: float = 0.38
    asymmetry: float = 0.0
    upper_curve: float = 1.0
    lower_curve: float = 0.95
    iris_offset_x: float = 0.0
    iris_offset_y: float = 0.0
    pupil_offset_x: float = 0.0
    pupil_offset_y: float = 0.0
    reflection_x: float = -0.22
    reflection_y: float = -0.20
    reflection_size: float = 0.11
    reflection_strength: float = 0.35
    rotation_deg: float = 0.0
    # V1.10: independent depth rotation about the local interocular/alignment axis.
    # Unlike rotation_deg (2D roll around the view axis), this foreshortens the
    # ocular surface in the current 2D projection. It is inherited by ocular
    # children and can be combined with roll without changing gaze semantics.
    alignment_axis_rotation_deg: float = 0.0
    # V1.13: true ocular view-axis orientation. These are consumed by the 3D
    # globe layer; ``rotation_deg`` remains the backwards-compatible roll.
    ocular_yaw_deg: float = 0.0
    ocular_pitch_deg: float = 0.0
    shape: EyeShape = "almond"
    contour_irregularity: float = 0.0
    contour_wave_amplitude: float = 0.0
    contour_wave_frequency: float = 1.0
    contour_samples: int = 64
    canthus_roundness: float = 0.035
    # Independent corner controls. The legacy field remains the default source
    # of truth for backwards-compatible authoring; explicit values allow inner
    # and outer canthi to diverge without contaminating iris/pupil parameters.
    canthus_inner_roundness: float | None = None
    canthus_outer_roundness: float | None = None
    # Continuous canthus transition controls. Zero preserves the V1.4 bridge exactly;
    # higher values lengthen the endpoint tangent transition without changing the
    # semantic canthus coordinates. Inner and outer controls are independent.
    canthus_inner_transition: float = 0.0
    canthus_outer_transition: float = 0.0
    # V1.7: a real ocular corner is not represented by a thick closing cap by
    # default. The legacy finite-gap cubic remains available explicitly.
    canthus_inner_terminal: CanthusTerminalSpec = CanthusTerminalSpec()
    canthus_outer_terminal: CanthusTerminalSpec = CanthusTerminalSpec()
    # V1.6: four independent endpoint tangent profiles.  Their default
    # influence=0 keeps the exact V1.5 geometry while exposing the four actual
    # upper/lower junctions for later reference-calibrated authoring.
    canthus_inner_upper_profile: CanthusEndpointTangentProfile = CanthusEndpointTangentProfile()
    canthus_inner_lower_profile: CanthusEndpointTangentProfile = CanthusEndpointTangentProfile()
    canthus_outer_upper_profile: CanthusEndpointTangentProfile = CanthusEndpointTangentProfile()
    canthus_outer_lower_profile: CanthusEndpointTangentProfile = CanthusEndpointTangentProfile()
    # V1.19: explicit eyelid/globe surface-follow control. The previous V1.18
    # default lived inside the coupling kernel, which made calibration impossible
    # to audit or persist as an authoring parameter. It remains a neutral engine
    # default until human-approved pixel calibration supplies evidence.
    eyelid_surface_follow_strength: float = 0.10
    # Stylized medial epicanthic-fold strength. Zero means no explicit fold.
    epicanthic_fold: float = 0.0

    def __post_init__(self) -> None:
        nums = (
            self.width, self.height, self.opening, self.iris_ratio, self.pupil_ratio, self.asymmetry,
            self.upper_curve, self.lower_curve, self.iris_offset_x, self.iris_offset_y,
            self.pupil_offset_x, self.pupil_offset_y, self.reflection_x, self.reflection_y,
            self.reflection_size, self.reflection_strength, self.rotation_deg, self.alignment_axis_rotation_deg,
            self.ocular_yaw_deg, self.ocular_pitch_deg,
            self.contour_irregularity, self.contour_wave_amplitude, self.contour_wave_frequency, self.canthus_roundness, self.canthus_inner_transition, self.canthus_outer_transition, self.epicanthic_fold,
        )
        if not _finite(nums):
            raise ValueError("Eye parameters must be finite")
        if self.width <= 0 or self.height <= 0:
            raise ValueError("Eye width and height must be > 0")
        if not 0 <= self.opening <= 1:
            raise ValueError("opening must be within [0,1]")
        if not 0 < self.iris_ratio <= 1:
            raise ValueError("iris_ratio must be within (0,1]")
        if not 0 < self.pupil_ratio <= 1:
            raise ValueError("pupil_ratio must be within (0,1]")
        if not -1 <= self.asymmetry <= 1:
            raise ValueError("asymmetry must be within [-1,1]")
        if self.upper_curve <= 0 or self.lower_curve <= 0:
            raise ValueError("lid curves must be > 0")
        if not -89.9 <= self.alignment_axis_rotation_deg <= 89.9:
            raise ValueError("alignment_axis_rotation_deg must be within [-89.9,89.9]")
        if not -180.0 <= self.ocular_yaw_deg <= 180.0:
            raise ValueError("ocular_yaw_deg must be within [-180,180]")
        if not -90.0 <= self.ocular_pitch_deg <= 90.0:
            raise ValueError("ocular_pitch_deg must be within [-90,90]")
        if self.reflection_size < 0 or not 0 <= self.reflection_strength <= 1:
            raise ValueError("invalid reflection")
        if self.contour_irregularity < 0 or self.contour_wave_amplitude < 0 or self.contour_wave_frequency <= 0:
            raise ValueError("invalid contour variation")
        if self.shape not in {"almond", "round", "large_round", "ellipse", "narrow", "droopy", "sharp", "upturned", "downturned"}:
            raise ValueError("unknown eye shape")
        if not 0 <= self.canthus_roundness <= 0.2:
            raise ValueError("canthus_roundness must be within [0,0.2]")
        if not 0 <= self.canthus_inner_transition <= 1 or not 0 <= self.canthus_outer_transition <= 1:
            raise ValueError("canthus transitions must be within [0,1]")
        if not 0 <= self.eyelid_surface_follow_strength <= 1:
            raise ValueError("eyelid_surface_follow_strength must be within [0,1]")
        if not 0 <= self.epicanthic_fold <= 1:
            raise ValueError("epicanthic_fold must be within [0,1]")
        profiles = (
            self.canthus_inner_upper_profile, self.canthus_inner_lower_profile,
            self.canthus_outer_upper_profile, self.canthus_outer_lower_profile,
        )
        if not all(isinstance(profile, CanthusEndpointTangentProfile) for profile in profiles):
            raise TypeError("canthus endpoint profiles must be CanthusEndpointTangentProfile instances")
        terminals = (self.canthus_inner_terminal, self.canthus_outer_terminal)
        if not all(isinstance(terminal, CanthusTerminalSpec) for terminal in terminals):
            raise TypeError("canthus terminals must be CanthusTerminalSpec instances")
        if self.contour_samples < 16:
            raise ValueError("contour_samples must be >= 16")
        for name, value in (("canthus_inner_roundness", self.canthus_inner_roundness), ("canthus_outer_roundness", self.canthus_outer_roundness)):
            if value is not None and (not math.isfinite(value) or not 0 <= value <= 0.2):
                raise ValueError(f"{name} must be None or within [0,0.2]")

    @property
    def eye_roll_deg(self) -> float:
        """Canonical V1.13 name for the historical screen-plane roll."""
        return self.rotation_deg

    @property
    def effective_canthus_inner_roundness(self) -> float:
        return self.canthus_roundness if self.canthus_inner_roundness is None else self.canthus_inner_roundness

    @property
    def effective_canthus_outer_roundness(self) -> float:
        return self.canthus_roundness if self.canthus_outer_roundness is None else self.canthus_outer_roundness
