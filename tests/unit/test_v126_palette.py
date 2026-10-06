from __future__ import annotations

from dataclasses import replace
import pytest

from visual_engine.components.common import (
    BaseColorRole, Component, Palette, PaletteEntry, PaletteError, PaletteInheritance,
    PaletteOverridePolicy, PaletteSlot, PaletteSource, PaletteSourceKind, PaletteProvenance,
)
from visual_engine.runtime import RuntimeGraph, resolve_palette, palette_resolution_fingerprint, palette_invalidation
from visual_engine.runtime.color_spaces import ColorRGBA


def palette(**values):
    return Palette.from_srgb("root", {PaletteSlot[k.upper()]: v for k, v in values.items()})


def test_authored_palette_preserves_exact_srgb_and_canonicalizes():
    p = palette(primary="#AaBbCc80")
    e = p.get(PaletteSlot.PRIMARY)
    assert e is not None
    assert e.authored_representation.value == "#AaBbCc80"
    assert e.canonical_color == ColorRGBA.from_hex("#AaBbCc80")


def test_duplicate_slots_are_rejected_even_before_resolution():
    c = ColorRGBA.from_hex("#112233")
    with pytest.raises(PaletteError):
        Palette((PaletteEntry(PaletteSlot.PRIMARY, c), PaletteEntry(PaletteSlot.PRIMARY, c)),
                source=PaletteSource(PaletteSourceKind.GENERATED, "g", "root"),
                provenance=PaletteProvenance("root", "root", "g", ("root",), "generated-authority", "gen", "1"))


def test_generated_palette_requires_generator_and_no_authored_representation():
    with pytest.raises(PaletteError):
        Palette(
            (PaletteEntry(PaletteSlot.PRIMARY, ColorRGBA.from_hex("#112233")),),
            source=PaletteSource(PaletteSourceKind.GENERATED, "g", "root"),
            provenance=PaletteProvenance("root", "root", "g", ("root",)),
        )


def test_missing_slot_does_not_fallback_to_another_slot():
    root = Component("root", "object", palette=Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#112233"}))
    child = Component("child", "hand")
    root.add_child(child)
    result = resolve_palette(RuntimeGraph.from_component(root), "child", slot=PaletteSlot.ACCENT)
    assert result.status == "unresolved"
    assert result.selected_entry is None


def test_nearest_palette_is_one_whole_authority():
    root = Component("root", "object", palette=Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#112233", PaletteSlot.ACCENT: "#AABBCC"}))
    mid = Component("mid", "group", palette=Palette.from_srgb("mid", {PaletteSlot.PRIMARY: "#445566"}))
    child = Component("child", "hand")
    root.add_child(mid)
    mid.add_child(child)
    result = resolve_palette(RuntimeGraph.from_component(root), "child", slot=PaletteSlot.ACCENT)
    assert result.status == "unresolved"
    assert result.palette is None


def test_blocking_nearest_authority_cannot_be_bypassed():
    root = Component("root", "object", palette=Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#112233"}))
    mid = Component("mid", "group", palette=Palette.from_srgb("mid", {PaletteSlot.PRIMARY: "#445566"}, inheritance=PaletteInheritance(False)))
    child = Component("child", "hand")
    root.add_child(mid); mid.add_child(child)
    result = resolve_palette(RuntimeGraph.from_component(root), "child", slot=PaletteSlot.PRIMARY)
    assert result.status == "unresolved"


def test_inherit_wins_over_local_palette():
    root = Component("root", "object", palette=Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#112233"}, inheritance=PaletteInheritance(True, PaletteOverridePolicy.INHERIT_WINS)))
    child = Component("child", "hand", palette=Palette.from_srgb("child", {PaletteSlot.PRIMARY: "#AABBCC"}))
    root.add_child(child)
    result = resolve_palette(RuntimeGraph.from_component(root), "child", slot=PaletteSlot.PRIMARY)
    assert result.status == "resolved"
    assert result.selected_entry.authored_representation.value == "#112233"
    assert result.palette.provenance.authority_component_id == "root"


def test_reject_conflict_does_not_silently_choose_local():
    root = Component("root", "object", palette=Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#112233"}, inheritance=PaletteInheritance(True, PaletteOverridePolicy.REJECT_CONFLICT)))
    child = Component("child", "hand", palette=Palette.from_srgb("child", {PaletteSlot.PRIMARY: "#AABBCC"}))
    root.add_child(child)
    result = resolve_palette(RuntimeGraph.from_component(root), "child", slot=PaletteSlot.PRIMARY)
    assert result.status == "rejected"


def test_local_wins_palette_is_not_invalidated_by_ancestor_content():
    root = Component("root", "object", palette=Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#112233"}))
    child = Component("child", "hand", palette=Palette.from_srgb("child", {PaletteSlot.PRIMARY: "#AABBCC"}))
    root.add_child(child)
    graph = RuntimeGraph.from_component(root)
    assert palette_invalidation(graph, "child", "root")[0] is False


def test_sibling_does_not_invalidate_palette():
    root = Component("root", "object", palette=Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#112233"}))
    a = Component("a", "object")
    b = Component("b", "object")
    root.add_child(a); root.add_child(b)
    graph = RuntimeGraph.from_component(root)
    assert palette_invalidation(graph, "a", "b")[0] is False


def test_palette_fingerprint_excludes_geometry():
    root = Component("root", "object", palette=Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#112233"}))
    child = Component("child", "hand")
    root.add_child(child)
    graph = RuntimeGraph.from_component(root)
    before = palette_resolution_fingerprint(graph, "child")
    child.transform = replace(child.transform, x=99)
    child.geometry = replace(child.geometry, local_z=42)
    after = palette_resolution_fingerprint(graph, "child")
    assert before == after


def test_typed_palette_and_legacy_palette_authority_conflict():
    root = Component("root", "object", palette=Palette.from_srgb("root", {PaletteSlot.PRIMARY: "#112233"}))
    from visual_engine.components.common import AppearanceLayer
    root.add_appearance(AppearanceLayer("legacy", {"palette": ("#112233",)}))
    with pytest.raises(PaletteError):
        resolve_palette(RuntimeGraph.from_component(root), "root", slot=PaletteSlot.PRIMARY)
