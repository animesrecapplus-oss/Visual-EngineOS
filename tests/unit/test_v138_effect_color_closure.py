from __future__ import annotations

import pytest

from visual_engine.runtime import effects as effects_module
from visual_engine.runtime.effects import VisualEffect, resolve_effects
from visual_engine.runtime.effect_color import apply_effect_color
from visual_engine.runtime.color_spaces import ColorRGBA


def _color(value: str) -> ColorRGBA:
    return ColorRGBA.from_hex(value)


def _resolve_pair(first: VisualEffect, second: VisualEffect) -> tuple[str, str, float, float, float, tuple[VisualEffect, ...]]:
    return resolve_effects(
        (first, second),
        base_fill="#20304080",
        base_contour="#d0d0d040",
        base_opacity=1.0,
        base_visibility=1.0,
    )


def _expected_sequential(first: VisualEffect, second: VisualEffect, base: str) -> str:
    first_result = apply_effect_color(
        _color(base), _color(first.color), effect_alpha=first.alpha,
        lineage=(first.source_id, first.effect_id),
    )
    second_result = apply_effect_color(
        first_result.color, _color(second.color), effect_alpha=second.alpha,
        lineage=(first.source_id, first.effect_id, second.source_id, second.effect_id),
    )
    return second_result.color.to_hex(include_alpha=len(base) == 9)


def test_all_production_calls_use_one_alpha_authority(monkeypatch: pytest.MonkeyPatch):
    calls: list[dict] = []
    real = effects_module.apply_effect_color

    def spy(*args, **kwargs):
        calls.append(kwargs.copy())
        return real(*args, **kwargs)

    monkeypatch.setattr(effects_module, "apply_effect_color", spy)
    resolve_effects(
        (
            VisualEffect("shadow", "shadow", priority=1, alpha=.25, color="#00000080", source_id="src-a"),
            VisualEffect("tint", "tint", priority=2, alpha=.50, color="#ffffff10", source_id="src-b"),
        ),
        base_fill="#20304080", base_contour="#d0d0d040", base_opacity=1, base_visibility=1,
    )
    assert [call["effect_alpha"] for call in calls] == [.25, .25, .50, .50]
    assert all("effect_color" not in call for call in calls)
    assert [call["lineage"] for call in calls] == [
        ("src-a", "shadow"), ("src-a", "shadow"),
        ("src-a", "shadow", "src-b", "tint"),
        ("src-a", "shadow", "src-b", "tint"),
    ]


def test_effect_color_alpha_never_participates_even_across_multiple_effects():
    opaque = _resolve_pair(
        VisualEffect("a", "shadow", priority=1, alpha=.4, color="#ff0000ff"),
        VisualEffect("b", "tint", priority=2, alpha=.3, color="#00ff00ff"),
    )
    transparent = _resolve_pair(
        VisualEffect("a", "shadow", priority=1, alpha=.4, color="#ff000000"),
        VisualEffect("b", "tint", priority=2, alpha=.3, color="#00ff0000"),
    )
    assert opaque[:5] == transparent[:5]


@pytest.mark.parametrize("first_kind,second_kind", [
    ("shadow", "shadow"),
    ("tint", "tint"),
    ("shadow", "tint"),
    ("tint", "shadow"),
])
def test_successive_color_effects_follow_the_priority_order(first_kind: str, second_kind: str):
    first = VisualEffect("first", first_kind, priority=1, alpha=.37, color="#2418d0")
    second = VisualEffect("second", second_kind, priority=2, alpha=.61, color="#e6a20f")
    result = _resolve_pair(first, second)
    assert result[0] == _expected_sequential(first, second, "#20304080")
    assert result[1] == _expected_sequential(first, second, "#d0d0d040")
    assert tuple(e.effect_id for e in result[-1]) == ("first", "second")


def test_input_order_is_not_semantic_but_priority_is():
    a = VisualEffect("a", "shadow", priority=1, alpha=.35, color="#000000")
    b = VisualEffect("b", "tint", priority=2, alpha=.55, color="#ffcc00")
    forward = _resolve_pair(a, b)
    reversed_input = _resolve_pair(b, a)
    assert forward == reversed_input

    b_first = VisualEffect("b", "tint", priority=0, alpha=.55, color="#ffcc00")
    priority_changed = _resolve_pair(b_first, a)
    assert priority_changed[0] != forward[0]


def test_equal_priority_uses_effect_id_then_source_as_deterministic_tie_breaker():
    a = VisualEffect("a", "shadow", priority=1, alpha=.5, color="#000000", source_id="z")
    b = VisualEffect("b", "tint", priority=1, alpha=.5, color="#ffffff", source_id="a")
    first = _resolve_pair(a, b)
    second = _resolve_pair(b, a)
    assert first == second
    assert tuple(e.effect_id for e in first[-1]) == ("a", "b")


def test_duplicate_effect_ids_fail_closed_at_resolution():
    duplicate = (
        VisualEffect("dup", "shadow", alpha=.2, color="#000000", source_id="a"),
        VisualEffect("dup", "tint", alpha=.2, color="#ffffff", source_id="b"),
    )
    with pytest.raises(ValueError, match="effect IDs must be unique"):
        resolve_effects(duplicate, base_fill="#123456", base_contour="#abcdef", base_opacity=1, base_visibility=1)


def test_fill_and_contour_receive_identical_cumulative_lineage(monkeypatch: pytest.MonkeyPatch):
    # The production function applies each effect independently to fill and contour,
    # but both operations must carry the same ordered effect history.
    calls: list[tuple[str, ...]] = []
    real = effects_module._apply_canonical_effect

    def spy(base, effect, effect_color, *, lineage, effect_fingerprint=None, lineage_fingerprint=None):
        calls.append(lineage)
        return real(
            base, effect, effect_color, lineage=lineage,
            effect_fingerprint=effect_fingerprint, lineage_fingerprint=lineage_fingerprint,
        )

    # Patch the exact production seam rather than duplicating color math.
    monkeypatch.setattr(effects_module, "_apply_canonical_effect", spy)
    resolve_effects(
        (
            VisualEffect("a", "shadow", priority=1, alpha=.2, source_id="s1", color="#000000"),
            VisualEffect("b", "tint", priority=2, alpha=.3, source_id="s2", color="#ffffff"),
        ),
        base_fill="#123456", base_contour="#abcdef", base_opacity=1, base_visibility=1,
    )
    assert calls == [
        ("s1", "a"), ("s1", "a"),
        ("s1", "a", "s2", "b"), ("s1", "a", "s2", "b"),
    ]


def test_fingerprint_changes_for_color_alpha_order_source_id_and_version(monkeypatch: pytest.MonkeyPatch):
    base = _color("#304050")
    effect = _color("#a0b0c0")
    kwargs = dict(effect_alpha=.4, lineage=("source-a", "effect-a"))
    baseline = apply_effect_color(base, effect, **kwargs)

    assert baseline.fingerprint != apply_effect_color(base, _color("#a0b0c1"), **kwargs).fingerprint
    assert baseline.fingerprint != apply_effect_color(base, effect, effect_alpha=.41, lineage=kwargs["lineage"]).fingerprint
    assert baseline.fingerprint != apply_effect_color(base, effect, **{**kwargs, "lineage": ("source-a", "effect-a", "source-b", "effect-b")}).fingerprint
    assert baseline.fingerprint != apply_effect_color(base, effect, **{**kwargs, "lineage": ("source-b", "effect-a")}).fingerprint
    assert baseline.fingerprint != apply_effect_color(base, effect, **{**kwargs, "lineage": ("source-a", "effect-b")}).fingerprint

    import visual_engine.runtime.effect_color as module
    monkeypatch.setattr(module, "EFFECT_COLOR_OPERATION_VERSION", "test-version-change")
    changed_version = apply_effect_color(base, effect, **kwargs)
    assert baseline.fingerprint != changed_version.fingerprint


def test_external_effect_fingerprint_cannot_mask_a_color_change():
    first = apply_effect_color(
        _color("#102030"), _color("#405060"), effect_alpha=.5,
        lineage=("s", "e"), effect_fingerprint="external-1",
    )
    second = apply_effect_color(
        _color("#102030"), _color("#405061"), effect_alpha=.5,
        lineage=("s", "e"), effect_fingerprint="external-1",
    )
    assert first.effect_fingerprint != second.effect_fingerprint
    assert first.fingerprint != second.fingerprint
