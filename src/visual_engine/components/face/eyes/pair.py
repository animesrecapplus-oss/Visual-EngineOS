from __future__ import annotations

from dataclasses import dataclass
from dataclasses import replace
import math
from typing import Literal

from .gaze.solver import BinocularGazeSolution, BinocularGazeSolver, Gaze
from .geometry.types import EyeGeometry
from .morphology.spec import EyeParameters
from .appearance.spec import EyeAppearance
from .geometry_builder import build_eye_geometry
from .contracts.types import EyeState
from .profiles import OcularPresentationProfile, apply_ocular_presentation

PairMode = Literal["human_default", "free"]


@dataclass(frozen=True, slots=True)
class EyePairPolicy:
    """Defines how a paired eye set may deviate from bilateral identity.

    `human_default` keeps the structural and appearance definitions identical
    unless explicit per-eye appearance is supplied for legitimate differences
    such as heterochromia. Size/orientation asymmetry is controlled separately.
    """

    mode: PairMode = "human_default"
    max_width_ratio_delta: float = 0.12
    max_height_ratio_delta: float = 0.12
    max_rotation_delta_deg: float = 5.0
    max_alignment_axis_rotation_delta_deg: float = 5.0

    def __post_init__(self) -> None:
        if self.mode not in {"human_default", "free"}:
            raise ValueError("unknown pair mode")
        if not 0 <= self.max_width_ratio_delta < 1:
            raise ValueError("max_width_ratio_delta must be in [0,1)")
        if not 0 <= self.max_height_ratio_delta < 1:
            raise ValueError("max_height_ratio_delta must be in [0,1)")
        if not math.isfinite(self.max_rotation_delta_deg) or self.max_rotation_delta_deg < 0:
            raise ValueError("max_rotation_delta_deg must be finite and >= 0")
        if not math.isfinite(self.max_alignment_axis_rotation_delta_deg) or self.max_alignment_axis_rotation_delta_deg < 0:
            raise ValueError("max_alignment_axis_rotation_delta_deg must be finite and >= 0")


@dataclass(frozen=True, slots=True)
class EyePairSpec:
    """Two eye definitions with bilateral identity as the default contract."""

    base_parameters: EyeParameters = EyeParameters()
    left_parameters: EyeParameters | None = None
    right_parameters: EyeParameters | None = None
    base_appearance: EyeAppearance = EyeAppearance()
    left_appearance: EyeAppearance | None = None
    right_appearance: EyeAppearance | None = None
    policy: EyePairPolicy = EyePairPolicy()
    presentation_profile: OcularPresentationProfile | None = None
    expression: str = "neutral"

    def resolve_parameters(self) -> tuple[EyeParameters, EyeParameters]:
        base = self.base_parameters
        left = self.left_parameters or base
        right = self.right_parameters or base
        if self.presentation_profile is not None:
            dummy = EyeAppearance()
            base, _ = apply_ocular_presentation(base, dummy, self.presentation_profile)
            left, _ = apply_ocular_presentation(left, dummy, self.presentation_profile)
            right, _ = apply_ocular_presentation(right, dummy, self.presentation_profile)
        if self.policy.mode == "human_default":
            _validate_human_pair_morphology(base, left, right, self.policy)
        return left, right

    def resolve_appearance(self) -> tuple[EyeAppearance, EyeAppearance]:
        left = self.left_appearance or self.base_appearance
        right = self.right_appearance or self.base_appearance
        if self.presentation_profile is not None:
            _, left = apply_ocular_presentation(self.base_parameters, left, self.presentation_profile)
            _, right = apply_ocular_presentation(self.base_parameters, right, self.presentation_profile)
        return left, right


def _relative_delta(a: float, b: float) -> float:
    scale = max(abs(a), abs(b), 1e-12)
    return abs(a - b) / scale


def _validate_human_pair_morphology(
    base: EyeParameters,
    left: EyeParameters,
    right: EyeParameters,
    policy: EyePairPolicy,
) -> None:
    # These are structural/style-defining properties. A human default pair
    # shares them; bilateral size and small orientation differences are allowed.
    structural = (
        "shape", "iris_ratio", "pupil_ratio", "upper_curve", "lower_curve",
        "contour_irregularity", "contour_wave_amplitude", "contour_wave_frequency",
        "contour_samples",
    )
    for name in structural:
        if getattr(left, name) != getattr(right, name) or getattr(left, name) != getattr(base, name):
            raise ValueError(f"human_default eye pair mismatch in structural field: {name}")
    if _relative_delta(left.width, right.width) > policy.max_width_ratio_delta:
        raise ValueError("left/right eye width asymmetry exceeds pair policy")
    if _relative_delta(left.height, right.height) > policy.max_height_ratio_delta:
        raise ValueError("left/right eye height asymmetry exceeds pair policy")
    if abs(left.rotation_deg - right.rotation_deg) > policy.max_rotation_delta_deg:
        raise ValueError("left/right eye rotation asymmetry exceeds pair policy")
    if abs(left.alignment_axis_rotation_deg - right.alignment_axis_rotation_deg) > policy.max_alignment_axis_rotation_delta_deg:
        raise ValueError("left/right eye alignment-axis rotation asymmetry exceeds pair policy")


@dataclass(frozen=True, slots=True)
class EyePairGeometry:
    left: EyeGeometry
    right: EyeGeometry
    left_appearance: EyeAppearance
    right_appearance: EyeAppearance
    gaze: BinocularGazeSolution
    paired: bool
    morphology_match: bool
    appearance_match: bool


def _rotate_about(point: tuple[float, float], center: tuple[float, float], degrees: float) -> tuple[float, float]:
    """Rotate a pair anchor around the binocular midpoint in scene space."""
    angle = math.radians(degrees)
    c, s = math.cos(angle), math.sin(angle)
    dx, dy = point[0] - center[0], point[1] - center[1]
    return (center[0] + c * dx - s * dy, center[1] + s * dx + c * dy)


def _pair_axis_rotation(left: EyeParameters, right: EyeParameters) -> float:
    """Resolve the common binocular axis from the two ocular orientations.

    A human-default pair normally has identical rotations. For the permitted
    small asymmetry, the axis uses the arithmetic mean so the inter-eye line does
    not jump toward either eye. This is a placement rule, not a replacement for
    each eye's own local rotation.
    """
    return (left.rotation_deg + right.rotation_deg) * 0.5


def build_eye_pair(
    spec: EyePairSpec | None = None,
    *,
    left_center: tuple[float, float] = (-0.65, 0.0),
    right_center: tuple[float, float] = (0.65, 0.0),
    target: tuple[float, float] = (0.0, -1.0),
    left_state: EyeState = "normal",
    right_state: EyeState = "normal",
    strength: float = 1.0,
    amplitude: float = 1.0,
) -> EyePairGeometry:
    s = spec or EyePairSpec()
    left_params, right_params = s.resolve_parameters()
    left_app, right_app = s.resolve_appearance()
    # The pair rotation is a rigid parent-level transform. Rotating only each
    # eye's contour while leaving the binocular anchors horizontal produces the
    # exact V1.8 failure: the eyes look individually rotated but are no longer a
    # rotated pair. Rotate both centers around their midpoint before solving gaze.
    pair_midpoint = ((left_center[0] + right_center[0]) * 0.5, (left_center[1] + right_center[1]) * 0.5)
    pair_rotation = _pair_axis_rotation(left_params, right_params)
    resolved_left_center = _rotate_about(left_center, pair_midpoint, pair_rotation)
    resolved_right_center = _rotate_about(right_center, pair_midpoint, pair_rotation)
    pair_gaze = BinocularGazeSolver.solve(resolved_left_center, resolved_right_center, target)
    left = build_eye_geometry(
        left_params,
        center=resolved_left_center,
        state=left_state,
        gaze=Gaze(target=target, strength=strength, amplitude=amplitude),
        appearance=left_app,
        expression=s.expression,
        side="image_left",
    )
    right = build_eye_geometry(
        right_params,
        center=resolved_right_center,
        state=right_state,
        gaze=Gaze(target=target, strength=strength, amplitude=amplitude),
        appearance=right_app,
        expression=s.expression,
        side="image_right",
    )
    morphology_match = _morphology_signature(left_params) == _morphology_signature(right_params)
    appearance_match = _appearance_signature(left_app) == _appearance_signature(right_app)
    return EyePairGeometry(left, right, left_app, right_app, pair_gaze, s.policy.mode == "human_default", morphology_match, appearance_match)


def _morphology_signature(p: EyeParameters) -> tuple[object, ...]:
    return (
        p.shape, p.iris_ratio, p.pupil_ratio, p.upper_curve, p.lower_curve,
        p.asymmetry, p.contour_irregularity, p.contour_wave_amplitude,
        p.contour_wave_frequency, p.contour_samples,
        p.canthus_inner_terminal, p.canthus_outer_terminal,
    )


def _appearance_signature(a: EyeAppearance) -> tuple[object, ...]:
    return (
        a.sclera, a.conjunctiva_color, a.outline, a.iris, a.lashes, a.eyebrow,
        a.reflection, a.reflection_opacity, a.reflection_marks, a.sclera_spots,
        a.under_eye_marks, a.stress_intensity, a.eyelid, a.lash_shadow, a.lower_lashes, a.caruncle,
    )


def make_heterochromic_pair(
    base_parameters: EyeParameters,
    left_appearance: EyeAppearance,
    right_iris_color: str,
) -> EyePairSpec:
    right_iris = replace(left_appearance.iris, color=right_iris_color)
    right_appearance = replace(left_appearance, iris=right_iris)
    return EyePairSpec(
        base_parameters=base_parameters,
        base_appearance=left_appearance,
        left_appearance=left_appearance,
        right_appearance=right_appearance,
    )
