from __future__ import annotations

from dataclasses import dataclass, replace
from typing import Literal

from .appearance.spec import EyeAppearance
from .morphology.spec import EyeParameters
from .lashes.spec import LashSpec
from .eyebrow.spec import BrowSpec

AgeGroup = Literal["young_child", "child", "adult", "elder"]
Presentation = Literal["neutral", "feminine_coded", "masculine_coded"]


@dataclass(frozen=True, slots=True)
class OcularPresentationProfile:
    """Visual parameter profile, not a biological or identity classifier.

    The engine never infers sex/gender from pixels. These profiles are explicit
    authoring choices used to produce different visual presentations. Their values
    are deliberately modest and remain overridable by the entity's own morphology.
    """
    age_group: AgeGroup = "adult"
    presentation: Presentation = "neutral"
    iris_scale_delta: float = 0.0
    opening_delta: float = 0.0
    upper_lid_delta: float = 0.0
    lower_lid_delta: float = 0.0
    lash_density_delta: float = 0.0
    lash_length_scale: float = 1.0
    lower_lash_density_delta: float = 0.0
    lower_lash_length_scale: float = 1.0
    brow_thickness_scale: float = 1.0
    brow_length_scale: float = 1.0

    def __post_init__(self) -> None:
        if self.age_group not in {"young_child", "child", "adult", "elder"}:
            raise ValueError("unknown age_group")
        if self.presentation not in {"neutral", "feminine_coded", "masculine_coded"}:
            raise ValueError("unknown presentation")
        vals = (self.iris_scale_delta, self.opening_delta, self.upper_lid_delta,
                self.lower_lid_delta, self.lash_density_delta, self.lash_length_scale,
                self.brow_thickness_scale, self.brow_length_scale)
        import math
        if not all(math.isfinite(float(v)) for v in vals):
            raise ValueError("profile values must be finite")
        if self.lash_length_scale <= 0 or self.lower_lash_length_scale <= 0 or self.brow_thickness_scale <= 0 or self.brow_length_scale <= 0:
            raise ValueError("profile scales must be > 0")

    @classmethod
    def preset(cls, age_group: AgeGroup = "adult", presentation: Presentation = "neutral") -> "OcularPresentationProfile":
        # These are restrained visual presets. They are not claims that every human
        # of an age/presentation has these features.
        values = {
            ("young_child", "neutral"): dict(iris_scale_delta=.10, opening_delta=.08, upper_lid_delta=.02, lower_lid_delta=.02),
            ("child", "neutral"): dict(iris_scale_delta=.06, opening_delta=.05),
            ("adult", "neutral"): {},
            ("elder", "neutral"): dict(iris_scale_delta=-.02, opening_delta=-.08, upper_lid_delta=-.02, lower_lid_delta=-.04),
            ("adult", "feminine_coded"): dict(opening_delta=.02, lash_density_delta=.18, lash_length_scale=1.18, lower_lash_density_delta=.04, lower_lash_length_scale=1.04, brow_length_scale=1.04),
            ("adult", "masculine_coded"): dict(opening_delta=-.01, lash_density_delta=-.20, lash_length_scale=.85, lower_lash_density_delta=-.05, lower_lash_length_scale=.90, brow_thickness_scale=1.22),
            ("child", "feminine_coded"): dict(iris_scale_delta=.06, opening_delta=.05, lash_density_delta=.08, lash_length_scale=1.05),
            ("child", "masculine_coded"): dict(iris_scale_delta=.06, opening_delta=.04),
            ("elder", "feminine_coded"): dict(iris_scale_delta=-.02, opening_delta=-.06, lash_density_delta=.05, lower_lash_density_delta=.02),
            ("elder", "masculine_coded"): dict(iris_scale_delta=-.02, opening_delta=-.08, lash_density_delta=-.10, lower_lash_density_delta=-.04, brow_thickness_scale=1.12),
            ("young_child", "feminine_coded"): dict(iris_scale_delta=.10, opening_delta=.08, lash_density_delta=.08),
            ("young_child", "masculine_coded"): dict(iris_scale_delta=.10, opening_delta=.07),
        }
        return cls(age_group=age_group, presentation=presentation, **values[(age_group, presentation)])


def apply_ocular_presentation(
    parameters: EyeParameters,
    appearance: EyeAppearance,
    profile: OcularPresentationProfile,
) -> tuple[EyeParameters, EyeAppearance]:
    """Apply a profile as bounded deltas while preserving entity-level overrides."""
    opening = min(1.0, max(0.0, parameters.opening + profile.opening_delta))
    iris_ratio = min(1.0, max(.001, parameters.iris_ratio + profile.iris_scale_delta))
    p = replace(parameters, opening=opening, iris_ratio=iris_ratio,
                upper_curve=max(.05, parameters.upper_curve + profile.upper_lid_delta),
                lower_curve=max(.05, parameters.lower_curve + profile.lower_lid_delta))
    lashes = replace(
        appearance.lashes,
        density=min(1.0, max(0.0, appearance.lashes.density + profile.lash_density_delta)),
        length=appearance.lashes.length * profile.lash_length_scale,
    )
    lower_lashes = replace(
        appearance.lower_lashes,
        density=min(1.0, max(0.0, appearance.lower_lashes.density + profile.lower_lash_density_delta)),
        length=appearance.lower_lashes.length * profile.lower_lash_length_scale,
    )
    brow = replace(
        appearance.eyebrow,
        thickness=appearance.eyebrow.thickness * profile.brow_thickness_scale,
        length=appearance.eyebrow.length * profile.brow_length_scale,
    )
    return p, replace(appearance, lashes=lashes, lower_lashes=lower_lashes, eyebrow=brow)
