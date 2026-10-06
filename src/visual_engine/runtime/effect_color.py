from __future__ import annotations

"""Canonical boundary for the engine's first real downstream color operation.

V1.34 closes the gap identified by the V1.32/V1.33 audits: ``shadow`` and
``tint`` effects are an existing production color transformation.  They do not
consume the typed COLOR resolver directly, but they are a genuine downstream
consumer of the resolved visual fill/contour colors.

The historical operation interpolated encoded 8-bit sRGB channels.  That is an
*art-directed effect semantic*, not linear-light compositing.  V1.34 therefore
makes that space explicit instead of silently changing the visual result:

    input:       canonical linear-sRGB ``ColorRGBA``
    effect:      canonical linear-sRGB ``ColorRGBA`` + independent effect alpha
    calculation: quantized 8-bit encoded sRGB RGB channels
    output:      canonical linear-sRGB ``ColorRGBA``
    alpha:       base alpha is preserved; effect.color alpha is ignored because
                 ``VisualEffect.alpha`` is the sole effect-opacity control

No gamut mapping, lighting, material response, premultiplied-alpha compositing,
or hidden renderer behavior belongs here.
"""

from dataclasses import dataclass
import math

from visual_engine.runtime.color_spaces import ColorRGBA
from visual_engine.runtime.identity import stable_digest

EFFECT_COLOR_OPERATION_ID = "effect.color.srgb8-interpolation"
EFFECT_COLOR_OPERATION_VERSION = "1"
EFFECT_COLOR_CALCULATION_SPACE = "srgb-encoded-8bit"


@dataclass(frozen=True, slots=True)
class EffectColorResult:
    """Immutable result and evidence for one color-effect application.

    The fingerprint is intentionally content-based so it can be used in
    diagnostics and cache/invalidation tests without relying on object identity.
    """

    color: ColorRGBA
    operation_id: str
    operation_version: str
    calculation_space: str
    base_fingerprint: str
    effect_fingerprint: str
    fingerprint: str
    lineage: tuple[str, ...]


def _validate_effect_alpha(alpha: float) -> float:
    alpha = float(alpha)
    if not math.isfinite(alpha) or not 0.0 <= alpha <= 1.0:
        raise ValueError("effect alpha must be finite and in [0,1]")
    return alpha


def _effect_dependency_fingerprint(effect_color: ColorRGBA, external_effect_fingerprint: str | None) -> str:
    """Fingerprint the actual effect color plus any external identity dependency.

    The color is always present, so an external fingerprint can add identity but
    can never mask a color mutation.
    """
    if external_effect_fingerprint is None:
        # Fast path used by the production resolver: preserve the original
        # ColorRGBA digest shape while avoiding a second digest per fill/contour.
        return stable_digest(effect_color)
    return stable_digest({
        "effect_color": effect_color,
        "external_effect_fingerprint": external_effect_fingerprint,
    })


def _lineage_fingerprint(lineage: tuple[str, ...]) -> str:
    """Return the deterministic dependency identity of an ordered lineage."""
    return stable_digest(lineage)


def _interpolate_srgb8(base: tuple[int, int, int], effect: tuple[int, int, int], alpha: float) -> tuple[int, int, int]:
    """Reproduce the established encoded-sRGB effect law exactly.

    Python's historical ``round`` behavior is intentional here.  Replacing it
    with half-up rounding would change a subset of existing artistic outputs.
    The operation is therefore versioned and tested against the pre-V1.34 law.
    """
    return tuple(
        round((1.0 - alpha) * source + alpha * target)
        for source, target in zip(base, effect)
    )  # type: ignore[return-value]


def apply_effect_color(
    base: ColorRGBA,
    effect_color: ColorRGBA,
    *,
    effect_alpha: float,
    lineage: tuple[str, ...] = (),
    effect_fingerprint: str | None = None,
    lineage_fingerprint: str | None = None,
) -> EffectColorResult:
    """Apply one shadow/tint color operation through an explicit sRGB8 seam.

    ``ColorRGBA`` remains the canonical representation at both sides of the
    operation.  Only the declared calculation space is quantized temporarily.
    Because the result is a convex interpolation of two in-gamut sRGB8 colors,
    the result is always representable in the canonical sRGB gamut.
    """
    if not isinstance(base, ColorRGBA) or not isinstance(effect_color, ColorRGBA):
        raise TypeError("base and effect_color must be ColorRGBA")
    effect_alpha = _validate_effect_alpha(effect_alpha)
    if any(not isinstance(item, str) or not item for item in lineage):
        raise ValueError("effect color lineage entries must be non-empty strings")

    # Alpha=0 is a strict identity path: do not quantize a canonical color that
    # the effect does not actually touch.  This matters for future non-hex callers.
    if effect_alpha == 0.0:
        result = base
    else:
        # Decode each endpoint exactly once.  The RGB channels participate in the
        # sRGB8 interpolation; only the base alpha is carried through.  Keeping the
        # decoded tuples local also avoids a second base.to_rgba8() conversion.
        base_rgba8 = base.to_rgba8()
        effect_rgba8 = effect_color.to_rgba8()
        rgb8 = _interpolate_srgb8(base_rgba8[:3], effect_rgba8[:3], effect_alpha)
        # The effect alpha is a color-effect opacity, not a replacement for the
        # target's alpha.  The historical function never used effect.color alpha.
        result = ColorRGBA.from_rgba8((*rgb8, base_rgba8[3]))

    base_fingerprint = stable_digest(base)
    # A caller-supplied effect fingerprint may carry external identity (for
    # example a database record), but it must never hide the actual effect color.
    # The color is therefore always part of the effective dependency fingerprint.
    resolved_effect_fingerprint = _effect_dependency_fingerprint(effect_color, effect_fingerprint)
    resolved_lineage_fingerprint = lineage_fingerprint or _lineage_fingerprint(lineage)
    fingerprint = stable_digest({
        "operation_id": EFFECT_COLOR_OPERATION_ID,
        "operation_version": EFFECT_COLOR_OPERATION_VERSION,
        "calculation_space": EFFECT_COLOR_CALCULATION_SPACE,
        "base_fingerprint": base_fingerprint,
        "effect_fingerprint": resolved_effect_fingerprint,
        "effect_alpha": effect_alpha,
        "lineage_fingerprint": resolved_lineage_fingerprint,
        "result": result,
    })
    return EffectColorResult(
        color=result,
        operation_id=EFFECT_COLOR_OPERATION_ID,
        operation_version=EFFECT_COLOR_OPERATION_VERSION,
        calculation_space=EFFECT_COLOR_CALCULATION_SPACE,
        base_fingerprint=base_fingerprint,
        effect_fingerprint=resolved_effect_fingerprint,
        fingerprint=fingerprint,
        lineage=lineage,
    )
