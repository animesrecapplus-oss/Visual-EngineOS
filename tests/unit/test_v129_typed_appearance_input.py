from __future__ import annotations

from dataclasses import replace

import pytest

from visual_engine.components.common import BaseColor, BaseColorRole, Component, Palette, PaletteSlot
from visual_engine.components.common.visual_contract import ContourContract, MaterialContract
from visual_engine.runtime import (
    AppearanceCompositionRequest,
    AppearanceDomain,
    CompositionMode,
    RuntimeGraph,
    TypedAppearanceInput,
    TypedAppearanceInputError,
    build_base_resolution_input_from_role,
    resolve_appearance_composition,
    resolve_base_domain,
)
from visual_engine.runtime.appearance_contract import AppearanceContribution
from visual_engine.runtime.appearance_role_bridge import RoleContributionSource, bridge_appearance_composition


def _graph_with_base(kind="object", color="#AaBbCc80"):
    root = Component("root", "object", base_color=BaseColor.from_srgb("root", color))
    target = Component("target", kind)
    root.add_child(target)
    return target, RuntimeGraph.from_component(root)


def _typed(target_id, graph, role=BaseColorRole.PRIMARY, mode=CompositionMode.BASE_THEN_PALETTE):
    composition = resolve_appearance_composition(graph, target_id, AppearanceCompositionRequest(role, mode))
    return TypedAppearanceInput.from_composition(
        composition,
        contour=ContourContract(),
        material=MaterialContract(),
        opacity=1.0,
        visibility=1.0,
    )


def test_canonical_typed_input_owns_role_and_derives_legacy_color():
    target, graph = _graph_with_base()
    data = _typed(target.id, graph)
    assert data.role_contribution.source is RoleContributionSource.BASE
    assert data.role_contribution.authored_srgb == "#AaBbCc80"
    assert data.legacy_base_color == "#AaBbCc80"
    assert data.fingerprint


def test_typed_input_fingerprint_is_geometry_independent():
    target, graph = _graph_with_base()
    before = _typed(target.id, graph).fingerprint
    target.transform = replace(target.transform, x=500, rotation_deg=37)
    target.geometry = replace(target.geometry, local_z=91)
    after = _typed(target.id, graph).fingerprint
    assert before == after


def test_typed_input_changes_when_role_authority_changes():
    target, graph = _graph_with_base(color="#112233")
    before = _typed(target.id, graph).fingerprint
    graph.get("root").component.base_color = BaseColor.from_srgb("root", "#445566")
    after = _typed(target.id, graph).fingerprint
    assert before != after


def test_typed_input_rejects_second_base_authority():
    target, graph = _graph_with_base()
    composition = resolve_appearance_composition(graph, target.id, AppearanceCompositionRequest(BaseColorRole.PRIMARY))
    with pytest.raises(TypedAppearanceInputError):
        TypedAppearanceInput.from_composition(
            composition,
            contour=ContourContract(), material=MaterialContract(), opacity=1, visibility=1,
            contributions=(AppearanceContribution("legacy", AppearanceDomain.BASE, "legacy", (("base_color", "#112233"),)),),
        )


def test_typed_input_tampering_is_fail_closed():
    target, graph = _graph_with_base()
    data = _typed(target.id, graph)
    with pytest.raises(TypedAppearanceInputError):
        replace(data, fingerprint="0" * 64)
    with pytest.raises(TypedAppearanceInputError):
        replace(data, visibility=0.5)


def test_legacy_appearance_input_is_derived_from_typed_authority():
    target, graph = _graph_with_base()
    data = _typed(target.id, graph)
    legacy = data.as_legacy_appearance_input()
    assert legacy.base_color == data.legacy_base_color
    assert legacy.role_contribution is data.role_contribution


def test_base_domain_consumes_typed_role_not_legacy_contribution():
    target, graph = _graph_with_base(color="#AaBbCc80")
    data = _typed(target.id, graph)
    domain_input = build_base_resolution_input_from_role(target.id, data.role_contribution)
    result = resolve_base_domain(domain_input)
    assert result.status.value == "resolved"
    assert result.resolved_fields[0].value == "#aabbcc80"
    assert result.provenance.role_bridge_fingerprint == data.role_contribution.fingerprint
    assert result.provenance.role_authority_component_id == "root"
    assert result.provenance.role_source_id == "base:root"
    assert result.provenance.role_lineage == ("root", target.id)


def test_role_bridge_becomes_explicit_domain_dependency():
    target, graph = _graph_with_base()
    data = _typed(target.id, graph)
    domain_input = build_base_resolution_input_from_role(target.id, data.role_contribution)
    assert any(d.name == "appearance_role_bridge" and d.digest == data.role_contribution.fingerprint for d in domain_input.dependencies)


def test_role_bridge_dependency_tampering_is_rejected():
    target, graph = _graph_with_base()
    data = _typed(target.id, graph)
    with pytest.raises(ValueError):
        build_base_resolution_input_from_role(
            target.id,
            data.role_contribution,
            dependencies={"appearance_role_bridge": "0" * 64},
        )


def test_domain_input_digest_changes_when_role_changes():
    target, graph = _graph_with_base(color="#112233")
    a = _typed(target.id, graph)
    ia = build_base_resolution_input_from_role(target.id, a.role_contribution)
    graph.get("root").component.base_color = BaseColor.from_srgb("root", "#445566")
    b = _typed(target.id, graph)
    ib = build_base_resolution_input_from_role(target.id, b.role_contribution)
    assert ia.input_digest != ib.input_digest
    assert ia.dependencies[-1].name == "appearance_role_bridge"


def test_domain_result_rejects_tampered_role_provenance():
    target, graph = _graph_with_base()
    data = _typed(target.id, graph)
    domain_input = build_base_resolution_input_from_role(target.id, data.role_contribution)
    result = resolve_base_domain(domain_input)
    bad = replace(result.provenance, role_bridge_fingerprint="0" * 64)
    tampered = replace(result, provenance=bad)
    from visual_engine.runtime.domain_resolution import validate_domain_resolution_result
    with pytest.raises(Exception):
        validate_domain_resolution_result(tampered, domain_input)


def test_palette_selected_role_is_still_typed_and_resolves_as_base_domain():
    root = Component("root", "object", palette=Palette.from_srgb("root", {PaletteSlot.ACCENT: "#F0A202"}))
    target = Component("hand", "hand")
    root.add_child(target)
    graph = RuntimeGraph.from_component(root)
    data = _typed(target.id, graph, BaseColorRole.ACCENT)
    assert data.role_contribution.source is RoleContributionSource.PALETTE
    result = resolve_base_domain(build_base_resolution_input_from_role(target.id, data.role_contribution))
    assert result.resolved_fields[0].value == "#f0a202"
    assert result.provenance.role_authority_component_id == "root"


def test_generic_non_ocular_object_hand_and_plant_paths_share_contract():
    root = Component("root", "object", base_color=BaseColor.from_srgb("root", "#123456"))
    object_child = Component("object", "object")
    hand = Component("hand", "hand")
    plant = Component("plant", "plant")
    root.add_child(object_child)
    root.add_child(hand)
    root.add_child(plant)
    graph = RuntimeGraph.from_component(root)
    fingerprints = []
    for child in (object_child, hand, plant):
        data = _typed(child.id, graph)
        result = resolve_base_domain(build_base_resolution_input_from_role(child.id, data.role_contribution))
        assert result.status.value == "resolved"
        fingerprints.append(data.fingerprint)
    assert len(set(fingerprints)) == 3


def test_component_persistence_round_trip_rebuilds_same_typed_role():
    from visual_engine.persistence.serialization import component_from_payload, component_payload, parameter_payload

    root = Component("root", "object", base_color=BaseColor.from_srgb("root", "#112233"))
    target = Component("hand", "hand")
    root.add_child(target)
    payload = component_payload(root)
    restored = component_from_payload(
        root.id,
        root.kind,
        None,
        parameter_payload(root.parameters),
        {},
        payload,
    )
    rebuilt_target = Component("hand", "hand")
    restored.add_child(rebuilt_target)
    restored_graph = RuntimeGraph.from_component(restored)
    original = _typed(target.id, RuntimeGraph.from_component(root))
    rebuilt = _typed(rebuilt_target.id, restored_graph)
    assert rebuilt.role_contribution.fingerprint == original.role_contribution.fingerprint
    assert rebuilt.fingerprint == original.fingerprint


def test_tampered_persisted_base_authority_cannot_reuse_old_typed_fingerprint():
    from visual_engine.persistence.serialization import component_from_payload, component_payload, parameter_payload

    root = Component("root", "object", base_color=BaseColor.from_srgb("root", "#112233"))
    target = Component("target", "object")
    root.add_child(target)
    payload = component_payload(root)
    payload["base_color"]["fingerprint"] = "0" * 64
    with pytest.raises(ValueError):
        component_from_payload(root.id, root.kind, None, parameter_payload(root.parameters), {}, payload)
