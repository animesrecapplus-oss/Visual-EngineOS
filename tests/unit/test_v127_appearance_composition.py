from __future__ import annotations

from dataclasses import replace
import pytest

from visual_engine.components.common import BaseColor, BaseColorRole, Component, Palette, PaletteInheritance, PaletteOverridePolicy, PaletteSlot
from visual_engine.runtime import (
    AppearanceCompositionError, AppearanceCompositionRequest, CompositionMode, CompositionSource,
    RuntimeGraph, appearance_composition_fingerprint, resolve_appearance_composition,
)


def graph_with(base=None, palette=None):
    root = Component("root", "object", base_color=base, palette=palette)
    child = Component("child", "hand")
    root.add_child(child)
    return root, child, RuntimeGraph.from_component(root)


def test_base_has_precedence_for_same_semantic_role():
    base = BaseColor.from_srgb("root", "#112233", role=BaseColorRole.PRIMARY)
    palette = Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#AABBCC"})
    _, _, graph = graph_with(base, palette)
    result = resolve_appearance_composition(graph, "child", AppearanceCompositionRequest(BaseColorRole.PRIMARY))
    assert result.status == "resolved"
    assert result.provenance.selected_source is CompositionSource.BASE
    assert result.selected_color is result.base_color
    assert result.palette_entry is not None


def test_palette_supplies_role_when_base_has_different_role():
    base = BaseColor.from_srgb("root", "#112233", role=BaseColorRole.SECONDARY)
    palette = Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#AABBCC"})
    _, _, graph = graph_with(base, palette)
    result = resolve_appearance_composition(graph, "child", AppearanceCompositionRequest(BaseColorRole.PRIMARY))
    assert result.status == "resolved"
    assert result.provenance.selected_source is CompositionSource.PALETTE
    assert result.palette_entry.authored_representation.value == "#AABBCC"


def test_base_only_does_not_fallback_to_palette():
    palette = Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#AABBCC"})
    _, _, graph = graph_with(None, palette)
    result = resolve_appearance_composition(graph, "child", AppearanceCompositionRequest(BaseColorRole.PRIMARY, CompositionMode.BASE_ONLY))
    assert result.status == "unresolved"


def test_palette_only_does_not_fallback_to_base():
    base = BaseColor.from_srgb("root", "#112233", role=BaseColorRole.PRIMARY)
    _, _, graph = graph_with(base, None)
    result = resolve_appearance_composition(graph, "child", AppearanceCompositionRequest(BaseColorRole.PRIMARY, CompositionMode.PALETTE_ONLY))
    assert result.status == "unresolved"


def test_missing_palette_slot_is_unresolved_not_mixed():
    palette = Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#AABBCC"})
    _, _, graph = graph_with(None, palette)
    result = resolve_appearance_composition(graph, "child", AppearanceCompositionRequest(BaseColorRole.ACCENT))
    assert result.status == "unresolved"


def test_reject_same_role_fails_closed():
    base = BaseColor.from_srgb("root", "#112233", role=BaseColorRole.PRIMARY)
    palette = Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#AABBCC"})
    _, _, graph = graph_with(base, palette)
    result = resolve_appearance_composition(graph, "child", AppearanceCompositionRequest(BaseColorRole.PRIMARY, CompositionMode.REJECT_SAME_ROLE))
    assert result.status == "rejected"
    assert result.selected_color is None


def test_contradictory_mode_request_is_rejected_at_boundary():
    with pytest.raises(AppearanceCompositionError):
        AppearanceCompositionRequest(BaseColorRole.PRIMARY, CompositionMode.BASE_ONLY, require_palette=True)


def test_background_role_has_no_implicit_primary_fallback():
    palette = Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#AABBCC"})
    _, _, graph = graph_with(None, palette)
    with pytest.raises(AppearanceCompositionError):
        resolve_appearance_composition(graph, "child", AppearanceCompositionRequest(BaseColorRole.BACKGROUND))


def test_requirements_are_explicit():
    palette = Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#AABBCC"})
    _, _, graph = graph_with(None, palette)
    result = resolve_appearance_composition(graph, "child", AppearanceCompositionRequest(BaseColorRole.PRIMARY, require_base=True))
    assert result.status == "unresolved"


def test_composition_fingerprint_is_geometry_independent():
    base = BaseColor.from_srgb("root", "#112233", role=BaseColorRole.PRIMARY)
    palette = Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#AABBCC"})
    _, child, graph = graph_with(base, palette)
    request = AppearanceCompositionRequest(BaseColorRole.PRIMARY)
    before = appearance_composition_fingerprint(graph, "child", request)
    child.transform = replace(child.transform, rotation_deg=37)
    child.geometry = replace(child.geometry, local_z=9)
    after = appearance_composition_fingerprint(graph, "child", request)
    assert before == after


def test_composition_fingerprint_changes_when_palette_changes():
    base = BaseColor.from_srgb("root", "#112233", role=BaseColorRole.PRIMARY)
    palette = Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#AABBCC"})
    root, _, graph = graph_with(base, palette)
    request = AppearanceCompositionRequest(BaseColorRole.PRIMARY)
    before = appearance_composition_fingerprint(graph, "child", request)
    root.palette = Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#DDEEFF"})
    after = appearance_composition_fingerprint(graph, "child", request)
    assert before != after


def test_composition_fingerprint_changes_when_base_changes():
    base = BaseColor.from_srgb("root", "#112233", role=BaseColorRole.PRIMARY)
    palette = Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#AABBCC"})
    root, _, graph = graph_with(base, palette)
    request = AppearanceCompositionRequest(BaseColorRole.PRIMARY)
    before = appearance_composition_fingerprint(graph, "child", request)
    root.base_color = BaseColor.from_srgb("root", "#DDEEFF", role=BaseColorRole.PRIMARY)
    after = appearance_composition_fingerprint(graph, "child", request)
    assert before != after


def test_non_ocular_component_uses_same_contract():
    palette = Palette.from_srgb("root", {PaletteSlot.ACCENT: "#FF8800"})
    root = Component("root", "object", palette=palette)
    hand = Component("hand", "hand")
    root.add_child(hand)
    result = resolve_appearance_composition(RuntimeGraph.from_component(root), "hand", AppearanceCompositionRequest(BaseColorRole.ACCENT))
    assert result.status == "resolved"
    assert result.target_component_id == "hand"
