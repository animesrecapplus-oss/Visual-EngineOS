from __future__ import annotations

from dataclasses import replace

import pytest

from visual_engine.components.common.base_color import BaseColor, BaseColorRole
from visual_engine.components.common.meta import Component
from visual_engine.components.common.palette import Palette, PaletteSlot
from visual_engine.components.common.visual_contract import ContourContract, MaterialContract
from visual_engine.runtime.appearance_contract import AppearanceDomain, AppearanceContribution
from visual_engine.runtime.appearance_composition import AppearanceCompositionRequest, resolve_appearance_composition
from visual_engine.runtime.base_resolution import (
    build_base_resolution_input_from_typed,
    resolve_base_domain,
    resolve_base_domain_from_typed,
)
from visual_engine.runtime.identity import stable_digest
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.typed_appearance_input import TypedAppearanceInput, TypedAppearanceInputError


def _typed(component_id: str, graph: RuntimeGraph, role: BaseColorRole = BaseColorRole.PRIMARY) -> TypedAppearanceInput:
    composition = resolve_appearance_composition(graph, component_id, AppearanceCompositionRequest(role))
    return TypedAppearanceInput.from_composition(
        composition,
        contour=ContourContract(),
        material=MaterialContract(),
        opacity=1.0,
        visibility=1.0,
    )


def _graph() -> tuple[RuntimeGraph, Component]:
    root = Component("root", "object", base_color=BaseColor.from_srgb("root", "#AaBbCc80"))
    target = Component("target", "object")
    root.add_child(target)
    return RuntimeGraph.from_component(root), target


def test_typed_envelope_is_the_direct_base_consumer_path():
    graph, target = _graph()
    typed = _typed(target.id, graph)
    direct = resolve_base_domain_from_typed(typed)
    explicit = resolve_base_domain(build_base_resolution_input_from_typed(typed))
    assert direct.result_digest == explicit.result_digest
    assert direct.resolved_fields[0].value == "#aabbcc80"


def test_typed_path_never_constructs_a_legacy_base_contribution():
    graph, target = _graph()
    typed = _typed(target.id, graph)
    domain_input = typed.to_base_domain_input()
    assert domain_input.role_contribution is typed.role_contribution
    assert domain_input.contributions == ()


def test_legacy_compatibility_adapter_and_typed_resolution_have_same_semantic_color():
    graph, target = _graph()
    typed = _typed(target.id, graph)
    legacy = typed.as_legacy_appearance_input()
    result = resolve_base_domain(typed.to_base_domain_input())
    assert legacy.base_color.lower() == result.resolved_fields[0].value
    assert legacy.role_contribution is typed.role_contribution


def test_tampering_typed_role_cannot_reuse_old_role_fingerprint():
    graph, target = _graph()
    typed = _typed(target.id, graph)
    with pytest.raises(Exception, match="role contribution fingerprint mismatch"):
        replace(typed.role_contribution, fingerprint="0" * 64)


def test_typed_input_rejects_second_base_authority():
    graph, target = _graph()
    role = _typed(target.id, graph).role_contribution
    contribution = AppearanceContribution("legacy-base", AppearanceDomain.BASE, "legacy", (("base_color", "#ffffff"),))
    payload = {
        "version": "1",
        "target_id": target.id,
        "role_contribution": role.fingerprint,
        "contour": ContourContract(),
        "material": MaterialContract(),
        "opacity": 1.0,
        "visibility": 1.0,
        "active_states": (),
        "appearance_layers": (),
        "contributions": (contribution,),
        "layer_resolution_digest": "",
    }
    with pytest.raises(TypedAppearanceInputError, match="second BASE"):
        TypedAppearanceInput(
            target.id, role, ContourContract(), MaterialContract(), 1.0, 1.0,
            contributions=(contribution,), fingerprint=stable_digest(payload)
        )


def test_unrelated_sibling_does_not_change_typed_or_domain_identity():
    graph, target = _graph()
    typed_before = _typed(target.id, graph)
    domain_before = typed_before.to_base_domain_input()
    sibling = graph.get("root").component
    sibling.add_child(Component("sibling", "plant", base_color=BaseColor.from_srgb("sibling", "#123456")))
    graph_after = RuntimeGraph.from_component(sibling)
    typed_after = _typed(target.id, graph_after)
    domain_after = typed_after.to_base_domain_input()
    assert typed_after.fingerprint == typed_before.fingerprint
    assert domain_after.input_digest == domain_before.input_digest


def test_geometry_change_is_not_a_typed_appearance_dependency():
    graph, target = _graph()
    typed_before = _typed(target.id, graph)
    target.geometry = {"x": 100, "y": 200, "w": 50, "h": 40}
    graph_after = RuntimeGraph.from_component(graph.get("root").component)
    typed_after = _typed(target.id, graph_after)
    assert typed_after.fingerprint == typed_before.fingerprint


def test_palette_selected_role_migrates_without_legacy_base_authority():
    root = Component("root", "object", palette=Palette.from_srgb("root", {PaletteSlot.ACCENT: "#F0A202"}))
    target = Component("hand", "hand")
    root.add_child(target)
    graph = RuntimeGraph.from_component(root)
    typed = _typed(target.id, graph, BaseColorRole.ACCENT)
    result = resolve_base_domain_from_typed(typed)
    assert result.resolved_fields[0].value == "#f0a202"
    assert result.provenance.role_source_id == typed.role_contribution.source_id


def test_domain_dependency_is_exactly_the_typed_role_fingerprint():
    graph, target = _graph()
    typed = _typed(target.id, graph)
    domain_input = typed.to_base_domain_input()
    matching = [d for d in domain_input.dependencies if d.name == "appearance_role_bridge"]
    assert len(matching) == 1
    assert matching[0].digest == typed.role_contribution.fingerprint


def test_conflicting_role_dependency_is_rejected():
    graph, target = _graph()
    typed = _typed(target.id, graph)
    with pytest.raises(Exception, match="contradicts typed role"):
        typed.to_base_domain_input(dependencies={"appearance_role_bridge": "0" * 64})
