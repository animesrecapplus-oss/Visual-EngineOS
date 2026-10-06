from __future__ import annotations

from dataclasses import replace

import pytest

from visual_engine.components.common import (
    BaseColor,
    BaseColorRole,
    Component,
    Palette,
    PaletteInheritance,
    PaletteOverridePolicy,
    PaletteSlot,
)
from visual_engine.components.common.visual_contract import ContourContract, MaterialContract
from visual_engine.runtime import (
    AppearanceCompositionRequest,
    AppearanceDomain,
    AppearanceRoleBridgeError,
    CompositionMode,
    RuntimeGraph,
    bridge_appearance_composition,
    bridge_fingerprint,
    bridge_to_appearance_input,
    resolve_appearance_composition,
    resolve_appearance_contract,
    role_bridge_invalidation,
)
from visual_engine.runtime.appearance_role_bridge import RoleContributionSource


def graph_with(*, base=None, palette=None):
    root = Component("root", "object", base_color=base, palette=palette)
    target = Component("target", "hand")
    root.add_child(target)
    return root, target, RuntimeGraph.from_component(root)


def request(role=BaseColorRole.PRIMARY, mode=CompositionMode.BASE_THEN_PALETTE):
    return AppearanceCompositionRequest(role, mode)


def test_base_bridge_preserves_authored_srgb_and_lineage():
    base = BaseColor.from_srgb("root", "#AaBbCc80", role=BaseColorRole.PRIMARY)
    _, target, graph = graph_with(base=base)
    result = resolve_appearance_composition(graph, target.id, request())
    bridge = bridge_appearance_composition(result)
    assert bridge.source is RoleContributionSource.BASE
    assert bridge.authored_srgb == "#AaBbCc80"
    assert bridge.legacy_base_color == "#AaBbCc80"
    assert bridge.lineage == ("root", "target")
    assert bridge.authority_component_id == "root"
    assert bridge.source_id == base.provenance.source_id


def test_palette_bridge_preserves_palette_provenance():
    palette = Palette.from_srgb("root", {PaletteSlot.ACCENT: "#F0A202"})
    _, target, graph = graph_with(palette=palette)
    result = resolve_appearance_composition(graph, target.id, request(BaseColorRole.ACCENT))
    bridge = bridge_appearance_composition(result)
    assert bridge.source is RoleContributionSource.PALETTE
    assert bridge.authored_srgb == "#F0A202"
    assert bridge.source_id == palette.provenance.source_id
    assert bridge.authority_component_id == "root"
    assert bridge.lineage == ("root", "target")


def test_generated_color_gets_deterministic_legacy_encoding_without_claiming_authored():
    base = BaseColor.generated_from_srgb(
        "root", "#12345680", generator_id="test-generator", generator_version="1"
    )
    _, target, graph = graph_with(base=base)
    result = resolve_appearance_composition(graph, target.id, request())
    bridge = bridge_appearance_composition(result)
    assert bridge.authored_srgb is None
    assert bridge.legacy_base_color == bridge.canonical_color.to_hex(include_alpha=True)


def test_inherited_base_retains_original_authored_representation():
    base = BaseColor.from_srgb("root", "#ABCDEF", role=BaseColorRole.PRIMARY)
    root, target, _ = graph_with(base=base)
    child = Component("grandchild", "object")
    target.add_child(child)
    graph = RuntimeGraph.from_component(root)
    result = resolve_appearance_composition(graph, target.id, request())
    bridge = bridge_appearance_composition(result)
    assert bridge.authored_srgb == "#ABCDEF"
    assert bridge.source is RoleContributionSource.BASE


def test_bridge_fingerprint_ignores_geometry():
    base = BaseColor.from_srgb("root", "#112233")
    root, target, graph = graph_with(base=base)
    result = resolve_appearance_composition(graph, target.id, request())
    before = bridge_fingerprint(result)
    target.transform = replace(target.transform, x=123, rotation_deg=27)
    target.geometry = replace(target.geometry, local_z=99)
    after = bridge_fingerprint(resolve_appearance_composition(graph, target.id, request()))
    assert before == after


def test_bridge_fingerprint_changes_when_selected_authority_changes():
    base = BaseColor.from_srgb("root", "#112233")
    root, target, graph = graph_with(base=base)
    before = bridge_fingerprint(resolve_appearance_composition(graph, target.id, request()))
    root.base_color = BaseColor.from_srgb("root", "#445566")
    after = bridge_fingerprint(resolve_appearance_composition(graph, target.id, request()))
    assert before != after


def test_bridge_rejects_unresolved_composition():
    _, target, graph = graph_with()
    result = resolve_appearance_composition(graph, target.id, request())
    assert result.status == "unresolved"
    with pytest.raises(AppearanceRoleBridgeError):
        bridge_appearance_composition(result)


def test_bridge_rejects_same_role_conflict():
    base = BaseColor.from_srgb("root", "#112233")
    palette = Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#445566"})
    _, target, graph = graph_with(base=base, palette=palette)
    result = resolve_appearance_composition(graph, target.id, request(mode=CompositionMode.REJECT_SAME_ROLE))
    assert result.status == "rejected"
    with pytest.raises(AppearanceRoleBridgeError):
        bridge_appearance_composition(result)


def test_legacy_appearance_input_is_derived_from_typed_bridge():
    base = BaseColor.from_srgb("root", "#AaBbCc80")
    _, target, graph = graph_with(base=base)
    result = resolve_appearance_composition(graph, target.id, request())
    data = bridge_to_appearance_input(
        result,
        contour=ContourContract(),
        material=MaterialContract(),
        opacity=1.0,
        visibility=1.0,
    )
    assert data.base_color == "#AaBbCc80"
    assert data.role_contribution is not None
    resolved = resolve_appearance_contract(data)
    assert resolved.base_color == "#aabbcc80"


def test_bridge_rejects_second_legacy_base_authority():
    from visual_engine.runtime.appearance_contract import AppearanceContribution

    base = BaseColor.from_srgb("root", "#112233")
    _, target, graph = graph_with(base=base)
    result = resolve_appearance_composition(graph, target.id, request())
    contribution = AppearanceContribution("legacy-base", AppearanceDomain.BASE, "legacy", (("base_color", "#445566"),))
    with pytest.raises(AppearanceRoleBridgeError):
        bridge_to_appearance_input(
            result,
            contour=ContourContract(), material=MaterialContract(), opacity=1, visibility=1,
            contributions=(contribution,),
        )


def test_tampered_role_contribution_fingerprint_is_rejected():
    base = BaseColor.from_srgb("root", "#112233")
    _, target, graph = graph_with(base=base)
    bridge = bridge_appearance_composition(resolve_appearance_composition(graph, target.id, request()))
    with pytest.raises(AppearanceRoleBridgeError):
        replace(bridge, fingerprint="0" * 64)


def test_tampered_role_contribution_cannot_change_legacy_color():
    base = BaseColor.from_srgb("root", "#112233")
    _, target, graph = graph_with(base=base)
    bridge = bridge_appearance_composition(resolve_appearance_composition(graph, target.id, request()))
    with pytest.raises(AppearanceRoleBridgeError):
        replace(bridge, legacy_base_color="#445566")


def test_role_bridge_invalidation_ignores_sibling():
    base = BaseColor.from_srgb("root", "#112233")
    root, target, _ = graph_with(base=base)
    sibling = Component("sibling", "object")
    root.add_child(sibling)
    graph = RuntimeGraph.from_component(root)
    affects, reasons = role_bridge_invalidation(graph, target.id, sibling.id, request())
    assert not affects
    assert reasons == ()


def test_base_only_mode_ignores_palette_mutation_for_bridge_invalidation():
    base = BaseColor.from_srgb("root", "#112233")
    palette = Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#445566"})
    root, target, graph = graph_with(base=base, palette=palette)
    root.palette = Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#778899"})
    affects, reasons = role_bridge_invalidation(
        graph, target.id, root.id, request(mode=CompositionMode.BASE_ONLY)
    )
    assert affects
    assert all(reason.startswith("BASE:") for reason in reasons)


def test_palette_only_mode_ignores_base_mutation_for_bridge_invalidation():
    base = BaseColor.from_srgb("root", "#112233")
    palette = Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#445566"})
    root, target, graph = graph_with(base=base, palette=palette)
    root.base_color = BaseColor.from_srgb("root", "#778899")
    affects, reasons = role_bridge_invalidation(
        graph, target.id, root.id, request(mode=CompositionMode.PALETTE_ONLY)
    )
    assert affects
    assert all(reason.startswith("PALETTE:") for reason in reasons)


def test_generic_non_ocular_component_uses_bridge():
    palette = Palette.from_srgb("root", {PaletteSlot.DETAIL: "#00AA88"})
    root = Component("root", "object", palette=palette)
    object_child = Component("prop", "object")
    root.add_child(object_child)
    result = resolve_appearance_composition(
        RuntimeGraph.from_component(root), object_child.id, request(BaseColorRole.DETAIL)
    )
    bridge = bridge_appearance_composition(result)
    assert bridge.target_id == "prop"
    assert bridge.source is RoleContributionSource.PALETTE


def test_palette_then_base_bridge_uses_palette_as_selected_authority():
    base = BaseColor.from_srgb("root", "#112233", role=BaseColorRole.PRIMARY)
    palette = Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#AABBCC"})
    _, target, graph = graph_with(base=base, palette=palette)
    result = resolve_appearance_composition(
        graph, target.id, request(mode=CompositionMode.PALETTE_THEN_BASE)
    )
    bridge = bridge_appearance_composition(result)
    assert bridge.source is RoleContributionSource.PALETTE
    assert bridge.authored_srgb == "#AABBCC"
    assert bridge.legacy_base_color == "#AABBCC"


def test_appearance_input_rejects_typed_role_and_legacy_string_drift():
    base = BaseColor.from_srgb("root", "#112233")
    _, target, graph = graph_with(base=base)
    result = resolve_appearance_composition(graph, target.id, request())
    bridge = bridge_appearance_composition(result)
    from visual_engine.runtime.appearance_contract import AppearanceResolutionInput
    with pytest.raises(ValueError, match="contradicts"):
        AppearanceResolutionInput(
            target_id=target.id,
            base_color="#445566",
            contour=ContourContract(),
            material=MaterialContract(),
            opacity=1.0,
            visibility=1.0,
            role_contribution=bridge,
        )
