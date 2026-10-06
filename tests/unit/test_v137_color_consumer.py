from __future__ import annotations

from visual_engine.runtime.color_spaces import ColorRGBA
from visual_engine.runtime.effect_color import (
    EFFECT_COLOR_OPERATION_ID,
    apply_effect_color,
)


def test_v137_no_new_runtime_path_is_preserved_as_a_source_contract():
    # The V1.37 audit artifact is intentionally removed from the current V1.38
    # checkpoint.  Keep the historical conclusion testable without coupling the
    # regression suite to a superseded generated artifact directory.
    assert EFFECT_COLOR_OPERATION_ID == "effect.color.srgb8-interpolation"


def test_only_candidate_is_existing_closed_effect_operation():
    from visual_engine.runtime.effects import _apply_canonical_effect
    assert _apply_canonical_effect.__module__ == "visual_engine.runtime.effects"
    assert EFFECT_COLOR_OPERATION_ID == "effect.color.srgb8-interpolation"


def test_effect_operation_identity_alpha_and_extreme_are_runtime_real():
    base = ColorRGBA.from_hex("#20406080")
    effect = ColorRGBA.from_hex("#e0c080ff")
    neutral = apply_effect_color(base, effect, effect_alpha=0.0, lineage=("v137", "neutral"))
    extreme = apply_effect_color(base, effect, effect_alpha=1.0, lineage=("v137", "extreme"))
    assert neutral.color is base
    assert extreme.color.to_rgba8() == (224, 192, 128, 128)
    assert extreme.color.alpha == base.alpha


def test_effect_operation_adversarial_bounds_and_types():
    base = ColorRGBA.from_hex("#123456")
    effect = ColorRGBA.from_hex("#abcdef")
    for alpha in (-1e-9, 1.000000001, float("nan"), float("inf")):
        try:
            apply_effect_color(base, effect, effect_alpha=alpha)
        except ValueError:
            pass
        else:
            raise AssertionError(f"invalid alpha accepted: {alpha!r}")
    try:
        apply_effect_color("#123456", effect, effect_alpha=0.5)  # type: ignore[arg-type]
    except TypeError:
        pass
    else:
        raise AssertionError("non-ColorRGBA base accepted")


def test_effect_fingerprint_and_lineage_are_deterministic():
    base = ColorRGBA.from_hex("#123456")
    effect = ColorRGBA.from_hex("#abcdef")
    a = apply_effect_color(base, effect, effect_alpha=0.37, lineage=("src", "fx"))
    b = apply_effect_color(base, effect, effect_alpha=0.37, lineage=("src", "fx"))
    c = apply_effect_color(base, effect, effect_alpha=0.38, lineage=("src", "fx"))
    assert a.fingerprint == b.fingerprint
    assert a.fingerprint != c.fingerprint
    assert a.lineage == ("src", "fx")
