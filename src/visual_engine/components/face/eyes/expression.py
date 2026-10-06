from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal

from .eyebrow.spec import BrowSpec
from .appearance.spec import EyeAppearance
from .morphology.spec import EyeParameters

ExpressionIntent = Literal[
    "neutral", "joy", "sadness", "anger", "fear", "surprise", "pain", "stress", "sleepy", "crying"
]


@dataclass(frozen=True, slots=True)
class OcularExpressionModifier:
    """Bounded, renderer-independent ocular expression deltas.

    These are authoring controls, not a claim that a real person's expression can
    be recovered from a fixed parameter recipe. The same intent can be overridden
    by entity morphology and state at higher layers.
    """
    opening_delta: float = 0.0
    upper_curve_delta: float = 0.0
    lower_curve_delta: float = 0.0
    brow_angle_delta_deg: float = 0.0
    brow_y_delta: float = 0.0
    brow_thickness_scale: float = 1.0


@dataclass(frozen=True, slots=True)
class OcularExpressionSolution:
    intent: ExpressionIntent
    parameters: EyeParameters
    appearance: EyeAppearance


class OcularExpressionSolver:
    """Resolve an ocular expression into geometry/appearance parameters."""

    _PRESETS: dict[ExpressionIntent, OcularExpressionModifier] = {
        "neutral": OcularExpressionModifier(),
        "joy": OcularExpressionModifier(opening_delta=0.04, upper_curve_delta=0.04, lower_curve_delta=0.06, brow_angle_delta_deg=2.0),
        "sadness": OcularExpressionModifier(opening_delta=-0.12, upper_curve_delta=-0.04, lower_curve_delta=-0.03, brow_angle_delta_deg=-7.0, brow_y_delta=-0.015),
        "anger": OcularExpressionModifier(opening_delta=-0.08, upper_curve_delta=-0.10, lower_curve_delta=-0.02, brow_angle_delta_deg=-14.0, brow_y_delta=0.01, brow_thickness_scale=1.05),
        "fear": OcularExpressionModifier(opening_delta=0.16, upper_curve_delta=0.10, lower_curve_delta=0.08, brow_angle_delta_deg=8.0, brow_y_delta=-0.02),
        "surprise": OcularExpressionModifier(opening_delta=0.22, upper_curve_delta=0.12, lower_curve_delta=0.10, brow_angle_delta_deg=3.0, brow_y_delta=-0.06),
        "pain": OcularExpressionModifier(opening_delta=-0.18, upper_curve_delta=-0.10, lower_curve_delta=-0.08, brow_angle_delta_deg=-8.0, brow_y_delta=0.015),
        "stress": OcularExpressionModifier(opening_delta=-0.06, upper_curve_delta=-0.04, lower_curve_delta=-0.02, brow_angle_delta_deg=-4.0, brow_thickness_scale=1.03),
        "sleepy": OcularExpressionModifier(opening_delta=-0.34, upper_curve_delta=-0.12, lower_curve_delta=-0.08, brow_angle_delta_deg=-1.0),
        "crying": OcularExpressionModifier(opening_delta=-0.08, upper_curve_delta=-0.03, lower_curve_delta=0.03, brow_angle_delta_deg=-5.0),
    }

    @classmethod
    def solve(
        cls,
        parameters: EyeParameters,
        appearance: EyeAppearance,
        intent: ExpressionIntent = "neutral",
    ) -> OcularExpressionSolution:
        if intent not in cls._PRESETS:
            raise ValueError(f"unknown ocular expression: {intent}")
        m = cls._PRESETS[intent]
        p = replace(
            parameters,
            opening=min(1.0, max(0.0, parameters.opening + m.opening_delta)),
            upper_curve=max(0.05, parameters.upper_curve + m.upper_curve_delta),
            lower_curve=max(0.05, parameters.lower_curve + m.lower_curve_delta),
        )
        brow: BrowSpec = replace(
            appearance.eyebrow,
            angle_deg=appearance.eyebrow.angle_deg + m.brow_angle_delta_deg,
            y=appearance.eyebrow.y + m.brow_y_delta,
            thickness=appearance.eyebrow.thickness * m.brow_thickness_scale,
        )
        return OcularExpressionSolution(intent, p, replace(appearance, eyebrow=brow))
