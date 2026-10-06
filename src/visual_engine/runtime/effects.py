from __future__ import annotations

from dataclasses import dataclass
import math

from visual_engine.runtime.color_spaces import ColorRGBA
from visual_engine.runtime.effect_color import (
    EFFECT_COLOR_CALCULATION_SPACE,
    EFFECT_COLOR_OPERATION_ID,
    EFFECT_COLOR_OPERATION_VERSION,
    _effect_dependency_fingerprint,
    _lineage_fingerprint,
    apply_effect_color,
)

_EFFECT_KINDS = {"shadow", "occlusion", "tint", "opacity", "visibility"}


def _hex(value: str) -> str:
    if not isinstance(value, str) or len(value) not in (7, 9) or not value.startswith("#"):
        raise ValueError("effect color must be #RRGGBB or #RRGGBBAA")
    try:
        int(value[1:], 16)
    except ValueError as exc:
        raise ValueError("effect color must be hexadecimal") from exc
    return value.lower()


def _unit(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{name} must be finite and in [0,1]")
    return value


@dataclass(frozen=True, slots=True)
class VisualEffect:
    """Generic external visual effect, deliberately independent of geometry.

    Effects are resolved after base visual inheritance. ``priority`` orders
    non-commutative color effects; multiplicative opacity/visibility effects are
    mathematically order-independent but retain the same deterministic ordering
    for provenance.
    """
    effect_id: str
    kind: str
    priority: int = 0
    alpha: float = 0.0
    color: str = "#000000"
    opacity_factor: float = 1.0
    visibility_factor: float = 1.0
    source_id: str = "__external__"
    target_id: str | None = None
    metadata: tuple[tuple[str, str], ...] = ()

    def __post_init__(self) -> None:
        if not self.effect_id:
            raise ValueError("effect_id must not be empty")
        if self.kind not in _EFFECT_KINDS:
            raise ValueError(f"unsupported effect kind: {self.kind}")
        if not isinstance(self.priority, int):
            raise ValueError("effect priority must be an integer")
        _unit(self.alpha, "effect alpha")
        _hex(self.color)
        _unit(self.opacity_factor, "effect opacity_factor")
        _unit(self.visibility_factor, "effect visibility_factor")
        if not self.source_id:
            raise ValueError("effect source_id must not be empty")
        if self.target_id is not None and not self.target_id:
            raise ValueError("effect target_id must be non-empty when provided")
        if len(set(k for k, _ in self.metadata)) != len(self.metadata):
            raise ValueError("effect metadata keys must be unique")

    @property
    def precedence_key(self) -> tuple[int, str, str]:
        return (self.priority, self.effect_id, self.source_id)


def sort_effects(effects: tuple[VisualEffect, ...]) -> tuple[VisualEffect, ...]:
    return tuple(sorted(effects, key=lambda effect: effect.precedence_key))


def apply_shadow_color(base: str, effect: VisualEffect) -> str:
    """Compatibility adapter from legacy hex to the canonical effect operation.

    Internal V1.34 resolution no longer uses this string-based helper.  It remains
    solely so legacy callers can cross the boundary explicitly.
    """
    if effect.kind != "shadow" or effect.alpha == 0:
        return base.lower()
    result = apply_effect_color(
        ColorRGBA.from_hex(base),
        ColorRGBA.from_hex(effect.color),
        effect_alpha=effect.alpha,
        lineage=("legacy-shadow-adapter", effect.effect_id),
    )
    return result.color.to_hex(include_alpha=len(base) == 9)


def _apply_canonical_effect(
    base: ColorRGBA,
    effect: VisualEffect,
    effect_color: ColorRGBA,
    *,
    lineage: tuple[str, ...],
    effect_fingerprint: str | None = None,
    lineage_fingerprint: str | None = None,
) -> ColorRGBA:
    """Apply one real production color effect without a legacy color detour.

    ``lineage`` is the ordered color-effect history accumulated by
    :func:`resolve_effects`.  Alpha authority remains singular: only
    ``VisualEffect.alpha`` reaches ``apply_effect_color``.
    """
    return apply_effect_color(
        base,
        effect_color,
        effect_alpha=effect.alpha,
        lineage=lineage,
        effect_fingerprint=effect_fingerprint,
        lineage_fingerprint=lineage_fingerprint,
    ).color


def resolve_effects(
    effects: tuple[VisualEffect, ...],
    *,
    base_fill: str,
    base_contour: str,
    base_opacity: float,
    base_visibility: float,
) -> tuple[str, str, float, float, float, tuple[VisualEffect, ...]]:
    """Resolve visual effects with one explicit color-operation boundary.

    Color effects use the existing canonical ``ColorRGBA`` boundary and the explicit
    encoded-sRGB-8bit calculation law.  Successive color effects are applied in
    ``precedence_key`` order; their ordered source/effect IDs form cumulative lineage.
    Opacity/visibility remain separate scalar effects; no alpha compositing is hidden
    inside the color operation.
    """
    # Keep non-color effect paths allocation/conversion-free.  Canonical colors
    # are materialized lazily only when the first shadow/tint actually needs them.
    fill_color: ColorRGBA | None = None
    contour_color: ColorRGBA | None = None
    opacity, visibility = base_opacity, base_visibility
    shadow_alpha = 0.0
    effect_ids = [effect.effect_id for effect in effects]
    if len(effect_ids) != len(set(effect_ids)):
        raise ValueError("effect IDs must be unique within a resolved component")
    ordered = sort_effects(effects)
    color_lineage: tuple[str, ...] = ()
    for effect in ordered:
        if effect.kind in {"shadow", "tint"}:
            if fill_color is None:
                fill_color = ColorRGBA.from_hex(base_fill)
            if contour_color is None:
                contour_color = ColorRGBA.from_hex(base_contour)
            # Decode each effect color once: fill and contour share the same
            # immutable effect authority, so a second parse adds cost without
            # adding semantic isolation.
            effect_color = ColorRGBA.from_hex(effect.color)
            # The same immutable effect authority feeds fill and contour, so compute
            # its dependency fingerprint once instead of twice.
            effect_fingerprint = _effect_dependency_fingerprint(effect_color, None)
            # Carry the complete ordered color-effect lineage into each successive
            # operation.  This does not alter RGB output; it prevents two distinct
            # effect histories that happen to reach the same intermediate color from
            # collapsing to the same operation fingerprint.
            color_lineage = color_lineage + (effect.source_id, effect.effect_id)
            lineage_fingerprint = _lineage_fingerprint(color_lineage)
            fill_color = _apply_canonical_effect(
                fill_color, effect, effect_color, lineage=color_lineage,
                effect_fingerprint=effect_fingerprint, lineage_fingerprint=lineage_fingerprint,
            )
            contour_color = _apply_canonical_effect(
                contour_color, effect, effect_color, lineage=color_lineage,
                effect_fingerprint=effect_fingerprint, lineage_fingerprint=lineage_fingerprint,
            )
            shadow_alpha = 1.0 - (1.0 - shadow_alpha) * (1.0 - effect.alpha)
        elif effect.kind == "opacity":
            opacity *= effect.opacity_factor
        elif effect.kind == "visibility":
            visibility *= effect.visibility_factor
        elif effect.kind == "occlusion":
            visibility *= (1.0 - effect.alpha) * effect.visibility_factor
            opacity *= effect.opacity_factor
    resolved_fill = base_fill.lower() if fill_color is None else fill_color.to_hex(include_alpha=len(base_fill) == 9)
    resolved_contour = base_contour.lower() if contour_color is None else contour_color.to_hex(include_alpha=len(base_contour) == 9)
    return (
        resolved_fill,
        resolved_contour,
        max(0.0, min(1.0, opacity)),
        max(0.0, min(1.0, visibility)),
        shadow_alpha,
        ordered,
    )


__all__ = [
    "VisualEffect",
    "sort_effects",
    "apply_shadow_color",
    "resolve_effects",
    "EFFECT_COLOR_OPERATION_ID",
    "EFFECT_COLOR_OPERATION_VERSION",
    "EFFECT_COLOR_CALCULATION_SPACE",
]
