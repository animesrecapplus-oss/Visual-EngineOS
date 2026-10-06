from __future__ import annotations

import itertools

import pytest

from visual_engine.model import Component, VisualContract
from visual_engine.runtime import (
    EFFECT_COLOR_CALCULATION_SPACE,
    EFFECT_COLOR_OPERATION_ID,
    EFFECT_COLOR_OPERATION_VERSION,
    ColorRGBA,
    ResolutionContext,
    RuntimeGraph,
    VisualEffect,
    apply_effect_color,
    resolve_component,
    resolve_effects,
)


def _legacy_rgb(base: str, effect: str, alpha: float) -> str:
    def rgb(value: str) -> tuple[int, int, int]:
        return tuple(int(value[i:i + 2], 16) for i in (1, 3, 5))

    source = rgb(base)
    target = rgb(effect)
    output = tuple(round((1.0 - alpha) * a + alpha * b) for a, b in zip(source, target))
    return "#%02x%02x%02x" % output


def test_operation_contract_is_explicit_and_canonical_at_boundaries():
    result = apply_effect_color(
        ColorRGBA.from_hex("#12345680"),
        ColorRGBA.from_hex("#ffffff"),
        effect_alpha=.25,
        lineage=("component", "effect-1"),
    )
    assert result.operation_id == EFFECT_COLOR_OPERATION_ID
    assert result.operation_version == EFFECT_COLOR_OPERATION_VERSION
    assert result.calculation_space == EFFECT_COLOR_CALCULATION_SPACE
    assert result.color.to_hex(include_alpha=True) == "#4d678080"
    assert result.lineage == ("component", "effect-1")
    assert len(result.fingerprint) == 64


def test_neutral_alpha_is_strict_identity_without_quantizing_canonical_color():
    base = ColorRGBA(.123456, .234567, .345678, .456789)
    result = apply_effect_color(base, ColorRGBA.from_hex("#ffffff"), effect_alpha=0.0)
    assert result.color == base


def test_extreme_alpha_replaces_rgb_but_preserves_base_alpha():
    result = apply_effect_color(
        ColorRGBA.from_hex("#10203040"),
        ColorRGBA.from_hex("#a0b0c0ff"),
        effect_alpha=1.0,
    )
    assert result.color.to_hex(include_alpha=True) == "#a0b0c040"


def test_effect_color_alpha_is_not_a_second_opacity_authority():
    opaque = apply_effect_color(
        ColorRGBA.from_hex("#20406080"),
        ColorRGBA.from_hex("#ff0000"),
        effect_alpha=.5,
    )
    translucent_effect_color = apply_effect_color(
        ColorRGBA.from_hex("#20406080"),
        ColorRGBA.from_hex("#ff000040"),
        effect_alpha=.5,
    )
    assert opaque.color == translucent_effect_color.color


@pytest.mark.parametrize("base,effect,alpha", [
    ("#000000", "#ffffff", 0.1),
    ("#ffffff", "#000000", 0.5),
    ("#123456", "#ff0000", 0.25),
    ("#808080", "#00ff00", 0.75),
    ("#feffff", "#0000ff", 0.333),
])
def test_migrated_effect_preserves_established_encoded_srgb_visual_law(base, effect, alpha):
    resolved = resolve_effects(
        (VisualEffect("effect", "shadow", alpha=alpha, color=effect),),
        base_fill=base,
        base_contour="#000000",
        base_opacity=1.0,
        base_visibility=1.0,
    )
    assert resolved[0] == _legacy_rgb(base, effect, alpha)


def test_alpha_bearing_base_color_is_not_silently_stripped():
    resolved = resolve_effects(
        (VisualEffect("effect", "shadow", alpha=.5, color="#000000"),),
        base_fill="#33669980",
        base_contour="#ffffff40",
        base_opacity=1.0,
        base_visibility=1.0,
    )
    assert resolved[0].endswith("80")
    assert resolved[1].endswith("40")


def test_effect_operation_is_ordered_and_deterministic():
    a = VisualEffect("a", "shadow", priority=1, alpha=.25, color="#000000")
    b = VisualEffect("b", "tint", priority=2, alpha=.5, color="#ff0000")
    first = resolve_effects((a, b), base_fill="#123456", base_contour="#ffffff", base_opacity=1, base_visibility=1)
    second = resolve_effects((b, a), base_fill="#123456", base_contour="#ffffff", base_opacity=1, base_visibility=1)
    assert first == second


def test_effect_operation_is_independent_of_unrelated_sibling_resolution():
    root = Component("root", "root")
    a = Component("a", "child", visual=VisualContract(fill_color="#123456"))
    b = Component("b", "child", visual=VisualContract(fill_color="#123456"))
    root.add_child(a)
    root.add_child(b)
    graph = RuntimeGraph.from_component(root)
    effect = VisualEffect("shadow-a", "shadow", alpha=.5, color="#000000", target_id="a")
    ra = resolve_component(graph, "a", context=ResolutionContext(effects=(effect,)))
    rb = resolve_component(graph, "b", context=ResolutionContext(effects=(effect,)))
    assert ra.visual.effective_fill_color != rb.visual.effective_fill_color
    assert rb.visual.effective_fill_color == "#123456"


def test_color_effect_provenance_names_operation_and_calculation_space():
    root = Component("root", "root", visual=VisualContract(fill_color="#123456"))
    effect = VisualEffect("shadow", "shadow", alpha=.5, color="#000000")
    result = resolve_component(RuntimeGraph.from_component(root), "root", context=ResolutionContext(effects=(effect,)))
    steps = result.provenance.for_field("shadow")
    assert len(steps) == 1
    assert steps[0].policy == EFFECT_COLOR_OPERATION_ID
    assert "calculation_space=srgb-encoded-8bit" in steps[0].detail
    assert "operation_version=1" in steps[0].detail


def test_srgb8_migration_matches_a_broad_channel_sample():
    values = ("00", "01", "7f", "80", "fe", "ff")
    for r, g, b in itertools.product(values, repeat=3):
        base = f"#{r}{g}{b}"
        result = resolve_effects(
            (VisualEffect("sample", "shadow", alpha=.333, color="#123456"),),
            base_fill=base,
            base_contour="#000000",
            base_opacity=1.0,
            base_visibility=1.0,
        )
        assert result[0] == _legacy_rgb(base, "#123456", .333)
