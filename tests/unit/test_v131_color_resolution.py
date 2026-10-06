from dataclasses import replace

import pytest

from visual_engine.components.common import BaseColor, BaseColorRole, Component, Palette, PaletteSlot
from visual_engine.components.common.visual_contract import ContourContract, MaterialContract
from visual_engine.runtime.appearance_contract import AppearanceContribution, AppearanceDomain, DomainContractError
from visual_engine.runtime.appearance_composition import AppearanceCompositionRequest, CompositionMode, resolve_appearance_composition
from visual_engine.runtime.appearance_role_bridge import bridge_appearance_composition, RoleContributionSource
from visual_engine.runtime.color_resolution import (
    COLOR_RESOLVER_ID,
    COLOR_RESOLVER_VERSION,
    ColorResolutionError,
    TypedColorInput,
    build_color_resolution_input_from_typed,
    color_domain_fingerprint,
    color_domain_invalidation,
    resolve_color_domain,
    resolve_color_domain_from_typed,
)
from visual_engine.runtime.domain_resolution import DomainResolutionStatus, build_domain_resolution_input
from visual_engine.runtime.identity import stable_digest
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.typed_appearance_input import TypedAppearanceInput


def _base_graph(color="#AaBbCc80", *, role=BaseColorRole.PRIMARY):
    root = Component("root", "object", base_color=BaseColor.from_srgb("root", color, role=role))
    target = Component("target", "hand")
    root.add_child(target)
    return root, target, RuntimeGraph.from_component(root)


def _palette_graph(color="#F0A202", *, slot=PaletteSlot.ACCENT):
    root = Component("root", "object", palette=Palette.from_srgb("root", {slot: color}))
    target = Component("target", "hand")
    root.add_child(target)
    return root, target, RuntimeGraph.from_component(root)


def _typed(graph, target, role=BaseColorRole.PRIMARY, mode=CompositionMode.BASE_THEN_PALETTE, **kwargs):
    composition = resolve_appearance_composition(
        graph,
        target.id,
        AppearanceCompositionRequest(role, mode),
    )
    return TypedAppearanceInput.from_composition(
        composition,
        contour=kwargs.get("contour", ContourContract()),
        material=kwargs.get("material", MaterialContract()),
        opacity=kwargs.get("opacity", 1.0),
        visibility=kwargs.get("visibility", 1.0),
        active_states=kwargs.get("active_states", ()),
    )


def _field_map(result):
    return {field.name: field.value for field in result.resolved_fields}


def test_authored_base_is_resolved_as_canonical_color_without_hex_round_trip():
    _, target, graph = _base_graph("#AaBbCc80")
    typed = _typed(graph, target)
    result = resolve_color_domain_from_typed(typed)
    fields = _field_map(result)
    assert result.status is DomainResolutionStatus.RESOLVED
    assert fields["color"] is typed.role_contribution.canonical_color
    assert fields["role"] == "primary"
    assert fields["source"] == RoleContributionSource.BASE.value
    assert fields["authored_srgb"] == "#AaBbCc80"
    assert fields["color"].to_hex(include_alpha=True) == "#aabbcc80"


def test_palette_selected_role_is_a_first_class_color_authority():
    _, target, graph = _palette_graph("#F0A202")
    typed = _typed(graph, target, BaseColorRole.ACCENT)
    result = resolve_color_domain_from_typed(typed)
    fields = _field_map(result)
    assert fields["color"] is typed.role_contribution.canonical_color
    assert fields["source"] == RoleContributionSource.PALETTE.value
    assert fields["role"] == "accent"
    assert fields["authored_srgb"] == "#F0A202"


def test_generated_color_has_no_false_authored_representation():
    root = Component(
        "root",
        "object",
        base_color=BaseColor.generated_from_srgb(
            "root", "#12345680", generator_id="test", generator_version="1"
        ),
    )
    target = Component("target", "plant")
    root.add_child(target)
    typed = _typed(RuntimeGraph.from_component(root), target)
    fields = _field_map(resolve_color_domain_from_typed(typed))
    assert "authored_srgb" not in fields
    assert fields["color"].to_hex(include_alpha=True) == "#12345680"


def test_typed_color_projection_excludes_material_contour_opacity_and_state():
    _, target, graph = _base_graph("#112233")
    a = _typed(graph, target, material=MaterialContract(), opacity=1.0, active_states=())
    b = _typed(
        graph,
        target,
        material=MaterialContract(roughness=0.9, metallic=1.0),
        opacity=0.25,
        active_states=("damaged",),
    )
    assert color_domain_fingerprint(a) == color_domain_fingerprint(b)
    assert TypedColorInput.from_typed_appearance_input(a).fingerprint == TypedColorInput.from_typed_appearance_input(b).fingerprint


def test_color_output_changes_when_selected_role_authority_changes():
    root, target, graph = _base_graph("#112233")
    before = resolve_color_domain_from_typed(_typed(graph, target))
    root.base_color = BaseColor.from_srgb("root", "#445566")
    after = resolve_color_domain_from_typed(_typed(graph, target))
    assert before.result_digest != after.result_digest
    assert _field_map(before)["color"] != _field_map(after)["color"]


def test_geometry_and_unrelated_sibling_do_not_change_color_identity():
    root, target, _ = _base_graph("#112233")
    sibling = Component("sibling", "object")
    root.add_child(sibling)
    graph = RuntimeGraph.from_component(root)
    typed_before = _typed(graph, target)
    color_before = TypedColorInput.from_typed_appearance_input(typed_before).fingerprint
    target.transform = replace(target.transform, x=123.0, rotation_deg=27.0)
    target.geometry = replace(target.geometry, local_z=91.0)
    sibling.base_color = BaseColor.from_srgb("sibling", "#ffffff")
    graph_after = RuntimeGraph.from_component(root)
    typed_after = _typed(graph_after, target)
    assert color_before == TypedColorInput.from_typed_appearance_input(typed_after).fingerprint
    assert _field_map(resolve_color_domain_from_typed(typed_before))["color"] == _field_map(resolve_color_domain_from_typed(typed_after))["color"]


def test_color_input_preserves_exact_role_bridge_dependency_identity():
    _, target, graph = _base_graph("#112233")
    typed = _typed(graph, target)
    data = typed.to_color_domain_input(dependencies={"appearance_layers": stable_digest("layers")})
    assert dict((item.name, item.digest) for item in data.dependencies)["appearance_role_bridge"] == typed.role_contribution.fingerprint
    result = resolve_color_domain(data)
    assert result.provenance.role_bridge_fingerprint == typed.role_contribution.fingerprint
    assert result.provenance.role_authority_component_id == typed.role_contribution.authority_component_id
    assert result.provenance.role_source_id == typed.role_contribution.source_id
    assert result.provenance.role_lineage == typed.role_contribution.lineage


def test_contradictory_role_dependency_is_rejected():
    _, target, graph = _base_graph("#112233")
    typed = _typed(graph, target)
    with pytest.raises(DomainContractError, match="contradicts"):
        build_color_resolution_input_from_typed(
            TypedColorInput.from_typed_appearance_input(typed),
            dependencies={"appearance_role_bridge": "0" * 64},
        )


def test_tampered_typed_color_fingerprint_is_rejected():
    _, target, graph = _base_graph("#112233")
    typed_color = TypedColorInput.from_typed_appearance_input(_typed(graph, target))
    with pytest.raises(ColorResolutionError, match="fingerprint mismatch"):
        replace(typed_color, fingerprint="0" * 64).__post_init__()


def test_color_resolver_rejects_missing_typed_role_instead_of_falling_back_to_legacy_color():
    legacy = AppearanceContribution(
        "legacy-color", AppearanceDomain.COLOR, "legacy", (("base_color", "#112233"),)
    )
    data = build_domain_resolution_input(
        "target", AppearanceDomain.COLOR,
        contributions=(legacy,),
        resolver_id=COLOR_RESOLVER_ID,
        resolver_version=COLOR_RESOLVER_VERSION,
    )
    result = resolve_color_domain(data)
    assert result.status is DomainResolutionStatus.REJECTED
    assert result.unresolved_reasons[0].startswith("COLOR_NO_TYPED_ROLE:")


def test_typed_role_and_legacy_color_authority_cannot_coexist():
    _, target, graph = _base_graph("#112233")
    typed = TypedColorInput.from_typed_appearance_input(_typed(graph, target))
    legacy = AppearanceContribution(
        "legacy-color", AppearanceDomain.COLOR, "legacy", (("base_color", "#445566"),)
    )
    with pytest.raises(DomainContractError, match="cannot coexist"):
        build_domain_resolution_input(
            target.id,
            AppearanceDomain.COLOR,
            contributions=(legacy,),
            role_contribution=typed.role_contribution,
            resolver_id=COLOR_RESOLVER_ID,
            resolver_version=COLOR_RESOLVER_VERSION,
        )


def test_color_domain_rejects_material_and_lighting_inputs_at_domain_boundary():
    _, target, graph = _base_graph("#112233")
    role = _typed(graph, target).role_contribution
    material = AppearanceContribution("m", AppearanceDomain.MATERIAL, "m", (("roughness", 0.5),))
    lighting = AppearanceContribution("l", AppearanceDomain.LIGHTING, "l", (("intensity", 1.0),))
    with pytest.raises(DomainContractError):
        build_domain_resolution_input(
            target.id, AppearanceDomain.COLOR,
            contributions=(material,), role_contribution=role,
            resolver_id=COLOR_RESOLVER_ID, resolver_version=COLOR_RESOLVER_VERSION,
        )
    with pytest.raises(DomainContractError):
        build_domain_resolution_input(
            target.id, AppearanceDomain.COLOR,
            contributions=(lighting,), role_contribution=role,
            resolver_id=COLOR_RESOLVER_ID, resolver_version=COLOR_RESOLVER_VERSION,
        )


def test_color_resolver_rejects_wrong_domain_programming_error():
    _, target, graph = _base_graph("#112233")
    role = _typed(graph, target).role_contribution
    data = build_domain_resolution_input(
        target.id, AppearanceDomain.BASE, role_contribution=role,
        resolver_id=COLOR_RESOLVER_ID, resolver_version=COLOR_RESOLVER_VERSION,
    )
    with pytest.raises(ColorResolutionError):
        resolve_color_domain(data)


def test_color_result_is_deterministic_and_dependency_sensitive():
    _, target, graph = _base_graph("#112233")
    typed = _typed(graph, target)
    a = resolve_color_domain_from_typed(typed, dependencies={"layers": stable_digest("a")})
    b = resolve_color_domain_from_typed(typed, dependencies={"layers": stable_digest("a")})
    c = resolve_color_domain_from_typed(typed, dependencies={"layers": stable_digest("b")})
    assert a.result_digest == b.result_digest
    assert a.result_digest != c.result_digest
    assert a.dependency_digest != c.dependency_digest


def test_color_invalidation_ignores_sibling_and_geometry_but_tracks_selected_authority():
    root, target, _ = _base_graph("#112233")
    sibling = Component("sibling", "object")
    root.add_child(sibling)
    graph = RuntimeGraph.from_component(root)
    request = AppearanceCompositionRequest(BaseColorRole.PRIMARY)
    affects_sibling, reasons_sibling = color_domain_invalidation(graph, target.id, sibling.id, request)
    assert not affects_sibling
    assert reasons_sibling == ()
    affects_root, reasons_root = color_domain_invalidation(graph, target.id, root.id, request)
    assert affects_root
    assert reasons_root and all(reason.startswith("COLOR depends on selected role:") for reason in reasons_root)


def test_palette_only_color_invalidation_does_not_claim_base_authority():
    root, target, graph = _palette_graph("#F0A202", slot=PaletteSlot.ACCENT)
    root.base_color = BaseColor.from_srgb("root", "#112233", role=BaseColorRole.ACCENT)
    request = AppearanceCompositionRequest(BaseColorRole.ACCENT, CompositionMode.PALETTE_ONLY)
    affects, reasons = color_domain_invalidation(graph, target.id, root.id, request)
    assert affects
    assert reasons and all("PALETTE:" in reason for reason in reasons)


def test_color_result_preserves_alpha_without_compositing():
    _, target, graph = _base_graph("#20406080")
    result = resolve_color_domain_from_typed(_typed(graph, target))
    color = _field_map(result)["color"]
    assert color.alpha == pytest.approx(128 / 255)
    assert color.to_hex(include_alpha=True) == "#20406080"


def test_color_resolver_never_performs_gamut_mapping_or_channel_clipping():
    _, target, graph = _base_graph("#FF00FF")
    result = resolve_color_domain_from_typed(_typed(graph, target))
    color = _field_map(result)["color"]
    # The canonical ColorRGBA already enforces the linear-sRGB gamut; the COLOR
    # resolver must return that object unchanged rather than remapping it.
    assert color == _typed(graph, target).role_contribution.canonical_color
