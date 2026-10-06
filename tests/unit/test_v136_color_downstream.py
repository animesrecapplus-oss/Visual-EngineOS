from __future__ import annotations

import hashlib
from pathlib import Path

from visual_engine.components.common import BaseColor, BaseColorRole, Component, Palette, PaletteSlot
from visual_engine.components.common.visual_contract import ContourContract, MaterialContract
from visual_engine.runtime.appearance_composition import AppearanceCompositionRequest, resolve_appearance_composition
from visual_engine.runtime.color_resolution import resolve_color_domain_from_typed
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.typed_appearance_input import TypedAppearanceInput

ROOT = Path(__file__).parents[2]

COLOR_BASELINE_SHA256 = {
    "src/visual_engine/runtime/effect_color.py": "eb3c0f4fff2965fe0ba438feb9b5f89158c0eb6d54d01262c167ba97d6e497c4",
    "src/visual_engine/runtime/color_spaces.py": "bbe129db981fb83be3417797e23dccf652947b5691fe88071ce0b9b389a4288a",
    "src/visual_engine/runtime/effects.py": "72f708b3a56fde007713d50e9f96550fc1feb2aa57c2cab66ff0724e75e1192a",
}


def _typed(graph, target, role):
    composition = resolve_appearance_composition(
        graph, target.id, AppearanceCompositionRequest(role)
    )
    return TypedAppearanceInput.from_composition(
        composition,
        contour=ContourContract(),
        material=MaterialContract(),
        opacity=1.0,
        visibility=1.0,
    )


def _fields(result):
    return {field.name: field.value for field in result.resolved_fields}


def _audit():
    from tools.audit_v136_color_downstream import build_report
    return build_report()


def test_audit_proves_no_new_generic_color_transform_and_no_eye_dependency():
    data = _audit()
    assert data["semantic_conclusion"]["true_new_generic_color_transformations"] == []
    assert data["semantic_conclusion"]["new_runtime_algorithm_warranted"] is False
    assert data["semantic_conclusion"]["eye_ColorRGBA_dependency_count"] == 0
    assert data["space_operations_outside_canonical_files"] == []


def test_all_colorrgba_consumers_are_explicitly_classified():
    data = _audit()
    allowed = {
        "authority_and_representation_conversion",
        "palette_storage_selection_and_representation_conversion",
        "serialization_deserialization",
        "typed_bridge_and_compatibility_representation",
        "type_validation",
        "already_closed_effect_operation_compatibility",
        "public_api_export",
    }
    assert data["canonical_ColorRGBA_consumers"]
    assert {item["classification"] for item in data["canonical_ColorRGBA_consumers"]} <= allowed


def test_base_role_reaches_color_resolver_unchanged():
    root = Component("root", "object", base_color=BaseColor.from_srgb("root", "#AaBbCc80"))
    target = Component("target", "hand")
    root.add_child(target)
    graph = RuntimeGraph.from_component(root)
    typed = _typed(graph, target, BaseColorRole.PRIMARY)
    result = resolve_color_domain_from_typed(typed)
    fields = _fields(result)
    assert fields["color"] is typed.role_contribution.canonical_color
    assert fields["color"].to_hex(include_alpha=True) == "#aabbcc80"
    assert fields["authored_srgb"] == "#AaBbCc80"


def test_palette_selection_reaches_color_resolver_without_channel_arithmetic():
    root = Component("root", "object", palette=Palette.from_srgb("root", {PaletteSlot.ACCENT: "#F0A202"}))
    target = Component("target", "plant")
    root.add_child(target)
    graph = RuntimeGraph.from_component(root)
    typed = _typed(graph, target, BaseColorRole.ACCENT)
    result = resolve_color_domain_from_typed(typed)
    fields = _fields(result)
    assert fields["color"] is typed.role_contribution.canonical_color
    assert fields["source"] == "palette"
    assert fields["authored_srgb"] == "#F0A202"


def test_renderer_rgba_math_is_not_mislabeled_as_generic_color():
    data = _audit()
    assert data["renderer_audit"]["renderer_rgba_operations"]
    assert data["semantic_conclusion"]["renderer_operation_is_generic_COLOR"] is False


def test_oklab_distance_is_measurement_not_color_transformation():
    data = _audit()
    assert data["semantic_conclusion"]["oklab_distance_is_transform"] is False


def test_v148_refactor_preserves_the_frozen_color_runtime_boundary():
    for relative, expected in COLOR_BASELINE_SHA256.items():
        digest = hashlib.sha256((ROOT / relative).read_bytes()).hexdigest()
        assert digest == expected
