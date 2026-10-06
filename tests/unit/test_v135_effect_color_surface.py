from __future__ import annotations

from visual_engine.runtime.effects import VisualEffect, resolve_effects

def _audit():
    from tools.audit_v136_color_downstream import build_report
    return build_report()


def test_closed_effect_path_remains_visible_in_v136_audit():
    data = _audit()
    assert data["closed_effect_color_path"]["operation_id"] == "effect.color.srgb8-interpolation"


def test_shadow_and_tint_remain_one_closed_operation():
    data = _audit()
    assert data["closed_effect_color_path"]["operation_id"] == "effect.color.srgb8-interpolation"
    assert data["semantic_conclusion"]["true_new_generic_color_transformation_count"] == 0


def test_scalar_effects_do_not_change_rgb():
    for kind in ("opacity", "visibility", "occlusion"):
        result = resolve_effects(
            (VisualEffect(kind, kind, alpha=.5, opacity_factor=.7, visibility_factor=.6),),
            base_fill="#123456",
            base_contour="#abcdef",
            base_opacity=1.0,
            base_visibility=1.0,
        )
        assert result[0] == "#123456"
        assert result[1] == "#abcdef"


def test_closed_effect_source_is_explicitly_classified():
    data = _audit()
    assert data["closed_effect_color_path"]["classification"] == "closed_by_V1_34_V1_35"


def test_no_direct_rgb_arithmetic_remains_outside_color_boundary():
    data = _audit()
    assert data["generic_runtime_rgb_arithmetic_candidates"] == []


def test_scalar_effect_order_remains_deterministic():
    effects = (
        VisualEffect("visibility", "visibility", priority=2, visibility_factor=.6),
        VisualEffect("opacity", "opacity", priority=1, opacity_factor=.7),
        VisualEffect("occlusion", "occlusion", priority=3, alpha=.2),
    )
    a = resolve_effects(effects, base_fill="#123456", base_contour="#abcdef", base_opacity=1, base_visibility=1)
    b = resolve_effects(tuple(reversed(effects)), base_fill="#123456", base_contour="#abcdef", base_opacity=1, base_visibility=1)
    assert a == b
