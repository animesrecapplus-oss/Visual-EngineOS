from visual_engine.model import Component
from visual_engine.components.common.meta import AppearanceLayer
from visual_engine.components.common.visual_contract import ContourContract, MaterialContract
from visual_engine.runtime.appearance_contract import AppearanceDomain, build_component_appearance_input
from visual_engine.runtime.appearance_layers import (
    AppearanceLayerBinding, AppearanceLayerPolicy, LayerActivationMode,
    LayerConflictMode, resolve_appearance_layers,
)
from visual_engine.runtime.effects import VisualEffect


def component():
    c = Component(id="eye", kind="eye")
    c.add_appearance(AppearanceLayer("base", {"base_color": "#ffffff"}))
    c.add_appearance(AppearanceLayer("wet", {"roughness": 0.5}))
    c.add_appearance(AppearanceLayer("iris", {"pattern": "procedural"}))
    return c


def bindings():
    return (
        AppearanceLayerBinding("base", AppearanceDomain.BASE),
        AppearanceLayerBinding("wet", AppearanceDomain.MATERIAL, required_states=("wet",)),
        AppearanceLayerBinding("iris", AppearanceDomain.COLOR, priority=5),
    )


def test_only_explicitly_bound_local_layers_enter_contract():
    c = component()
    result = resolve_appearance_layers(c, bindings=bindings())
    assert [x.contribution_id for x in result.contributions] == ["layer:eye:base", "layer:eye:iris"]
    assert result.unresolved_layers == ()
    assert all(p.source_kind == "component.appearance" for p in result.provenance)


def test_missing_binding_fails_closed_as_unresolved_not_base_or_color():
    c = component()
    result = resolve_appearance_layers(c, bindings=bindings()[:1])
    assert result.unresolved_layers == ("iris", "wet")
    assert [x.domain for x in result.contributions] == [AppearanceDomain.BASE]


def test_declaration_order_is_preserved_and_priority_does_not_silently_reorder():
    c = component()
    result = resolve_appearance_layers(c, bindings=bindings())
    assert [x.layer_name for x in result.provenance] == ["base", "iris"]


def test_state_activation_requires_explicit_binding_and_resolved_state_input():
    c = component()
    inactive = resolve_appearance_layers(c, active_states=(), bindings=bindings())
    active = resolve_appearance_layers(c, active_states=("wet",), bindings=bindings())
    assert "layer:eye:wet" not in [x.contribution_id for x in inactive.contributions]
    assert "layer:eye:wet" in [x.contribution_id for x in active.contributions]


def test_any_state_activation_is_explicit():
    c = component()
    b = AppearanceLayerBinding("wet", AppearanceDomain.MATERIAL, required_states=("wet", "rain"), activation_mode=LayerActivationMode.ANY_STATE)
    result = resolve_appearance_layers(c, active_states=("rain",), bindings=(b,))
    assert len(result.contributions) == 1


def test_effects_become_typed_effect_contributions_without_reinterpretation():
    c = component()
    effect = VisualEffect("fx", "occlusion", priority=7, alpha=.4, opacity_factor=.8, visibility_factor=.9, source_id="hand", target_id="eye")
    result = resolve_appearance_layers(c, effects=(effect,), bindings=())
    assert result.contributions[0].domain is AppearanceDomain.EFFECT
    values = dict(result.contributions[0].values)
    assert values["kind"] == "occlusion"
    assert values["alpha"] == .4
    assert values["opacity_factor"] == .8


def test_explicit_conflict_policy_is_required_and_deterministic():
    c = Component(id="x", kind="test")
    c.add_appearance(AppearanceLayer("a", {"v": 1}))
    c.add_appearance(AppearanceLayer("b", {"v": 2}))
    bs = (
        AppearanceLayerBinding("a", AppearanceDomain.COLOR, priority=1, conflict_group="g"),
        AppearanceLayerBinding("b", AppearanceDomain.COLOR, priority=2, conflict_group="g"),
    )
    p = AppearanceLayerPolicy("g", LayerConflictMode.HIGHEST_PRIORITY)
    result = resolve_appearance_layers(c, bindings=bs, policies=(p,))
    assert [x.contribution_id for x in result.contributions] == ["layer:x:b"]
    assert any(d.action == "rejected" for d in result.decisions)


def test_conflict_group_without_policy_fails_closed():
    c = component()
    b = AppearanceLayerBinding("base", AppearanceDomain.BASE, conflict_group="missing")
    try:
        resolve_appearance_layers(c, bindings=(b,))
    except ValueError as exc:
        assert "no policy" in str(exc)
    else:
        raise AssertionError("missing conflict policy must fail closed")


def test_duplicate_layer_names_are_ambiguous():
    c = Component(id="x", kind="test")
    c.add_appearance(AppearanceLayer("same", {}))
    c.add_appearance(AppearanceLayer("same", {}))
    try:
        resolve_appearance_layers(c, bindings=(AppearanceLayerBinding("same", AppearanceDomain.BASE),))
    except ValueError as exc:
        assert "ambiguous" in str(exc)
    else:
        raise AssertionError("duplicate layer names must fail closed")


def test_no_implicit_inheritance_from_parent():
    parent = Component(id="parent", kind="face")
    parent.add_appearance(AppearanceLayer("skin", {"base_color": "#123456"}))
    child = Component(id="child", kind="eye")
    parent.add_child(child)
    result = resolve_appearance_layers(child, bindings=())
    assert result.contributions == ()
    assert result.unresolved_layers == ()


def test_bridge_enters_appearance_resolution_input():
    data, layer_result = build_component_appearance_input(
        component(), base_color="#ffffff", contour=ContourContract(), material=MaterialContract(),
        opacity=1, visibility=1, bindings=bindings(), active_states=("wet",),
    )
    assert data.target_id == "eye"
    assert len(data.contributions) == 3
    assert layer_result.dependency_digest
    assert data.layer_resolution_digest == layer_result.dependency_digest


def test_dependency_digest_changes_when_local_layer_changes_but_not_for_unrelated_component():
    c = component()
    a = resolve_appearance_layers(c, bindings=bindings())
    c2 = component()
    c2.appearance[0].values["base_color"] = "#000000"
    b = resolve_appearance_layers(c2, bindings=bindings())
    assert a.dependency_digest != b.dependency_digest
    unrelated = Component(id="other", kind="test")
    assert resolve_appearance_layers(unrelated, bindings=()).dependency_digest != a.dependency_digest


def test_effect_input_order_does_not_change_dependency_digest_or_contribution_order():
    c = component()
    e1 = VisualEffect("a", "opacity", priority=1, opacity_factor=.8, target_id="eye")
    e2 = VisualEffect("b", "visibility", priority=2, visibility_factor=.7, target_id="eye")
    first = resolve_appearance_layers(c, effects=(e1, e2), bindings=bindings())
    second = resolve_appearance_layers(c, effects=(e2, e1), bindings=bindings())
    assert first.dependency_digest == second.dependency_digest
    assert [x.contribution_id for x in first.contributions] == [x.contribution_id for x in second.contributions]
