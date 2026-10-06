import pytest

from visual_engine.components.common import (
    AlphaSemantics,
    BaseColor,
    BaseColorAuthoredRepresentation,
    BaseColorError,
    BaseColorInheritance,
    BaseColorOverridePolicy,
    BaseColorProvenance,
    BaseColorRole,
    BaseColorSource,
    BaseColorSourceKind,
    Component,
)
from visual_engine.runtime import (
    RuntimeGraph,
    adapt_legacy_base_color,
    base_color_invalidation,
    base_color_resolution_fingerprint,
    resolve_base_color,
)
from visual_engine.components.common.visual_contract import LocalTransform
from visual_engine.components.common.geometry_contract import GeometryContract, GeometryBounds


def test_authored_base_color_preserves_exact_srgb_and_stores_linear_canonical_color():
    color = BaseColor.from_srgb("object", "#A0b0C0")
    assert color.authored_representation == BaseColorAuthoredRepresentation("srgb", "#A0b0C0")
    assert color.source.kind is BaseColorSourceKind.AUTHORED
    assert color.canonical_color.red != 160 / 255
    assert color.canonical_color.red == pytest.approx(0.35153259950043936, rel=0.0, abs=1e-15)
    assert color.alpha_semantics is AlphaSemantics.OPAQUE
    assert len(color.fingerprint) == 64


def test_rgba_authored_alpha_is_preserved_without_compositing():
    color = BaseColor.from_srgb("object", "#10203080")
    assert color.authored_representation.value == "#10203080"
    assert color.canonical_color.alpha == pytest.approx(128 / 255)
    assert color.alpha_semantics is AlphaSemantics.UNASSOCIATED


def test_generated_base_requires_complete_generator_provenance():
    color = BaseColor.generated_from_srgb("object", "#112233", generator_id="palette-seed", generator_version="1")
    assert color.source.kind is BaseColorSourceKind.GENERATED
    assert color.authored_representation is None
    assert color.provenance.generator_id == "palette-seed"
    assert color.provenance.generator_version == "1"


def test_inherited_color_preserves_original_authority_and_authored_representation():
    root_color = BaseColor.from_srgb("root", "#ABCDEF")
    child_color = root_color.inherited_for("child", lineage=("root", "middle", "child"))
    assert child_color.source.kind is BaseColorSourceKind.INHERITED
    assert child_color.source.component_id == "root"
    assert child_color.provenance.authority_component_id == "root"
    assert child_color.provenance.target_component_id == "child"
    assert child_color.provenance.lineage == ("root", "middle", "child")
    assert child_color.authored_representation.value == "#ABCDEF"
    assert child_color.canonical_color == root_color.canonical_color


def test_inheritance_can_be_explicitly_blocked():
    color = BaseColor.from_srgb(
        "root", "#123456",
        inheritance=BaseColorInheritance(allow_children=False),
    )
    root = Component("root", "object", base_color=color)
    child = Component("child", "object")
    root.add_child(child)
    result = resolve_base_color(RuntimeGraph.from_component(root), "child")
    assert result.status == "unresolved"
    assert "blocks inheritance" in result.reason


def test_local_authority_overrides_inherited_authority_by_default():
    root = Component("root", "object", base_color=BaseColor.from_srgb("root", "#111111"))
    child = Component("child", "object", base_color=BaseColor.from_srgb("child", "#222222"))
    root.add_child(child)
    result = resolve_base_color(RuntimeGraph.from_component(root), "child")
    assert result.status == "resolved"
    assert result.color.source.kind is BaseColorSourceKind.AUTHORED
    assert result.color.source.component_id == "child"


def test_inherit_wins_is_explicit_and_deterministic():
    root = Component(
        "root", "object",
        base_color=BaseColor.from_srgb(
            "root", "#111111",
            inheritance=BaseColorInheritance(override_policy=BaseColorOverridePolicy.INHERIT_WINS),
        ),
    )
    child = Component("child", "object", base_color=BaseColor.from_srgb("child", "#222222"))
    root.add_child(child)
    result = resolve_base_color(RuntimeGraph.from_component(root), "child")
    assert result.status == "resolved"
    assert result.color.source.kind is BaseColorSourceKind.INHERITED
    assert result.color.canonical_color == root.base_color.canonical_color
    assert result.reason == "nearest ancestor INHERIT_WINS"


def test_reject_conflict_does_not_silently_choose_a_source():
    root = Component(
        "root", "object",
        base_color=BaseColor.from_srgb(
            "root", "#111111",
            inheritance=BaseColorInheritance(override_policy=BaseColorOverridePolicy.REJECT_CONFLICT),
        ),
    )
    root.add_child(Component("child", "object", base_color=BaseColor.from_srgb("child", "#222222")))
    result = resolve_base_color(RuntimeGraph.from_component(root), "child")
    assert result.status == "rejected"
    assert result.color is None


def test_nearest_authority_is_used_and_lineage_is_complete():
    root = Component("root", "object", base_color=BaseColor.from_srgb("root", "#111111"))
    middle = Component("middle", "object", base_color=BaseColor.from_srgb("middle", "#222222"))
    leaf = Component("leaf", "object")
    root.add_child(middle)
    middle.add_child(leaf)
    result = resolve_base_color(RuntimeGraph.from_component(root), "leaf")
    assert result.color.source.component_id == "middle"
    assert result.color.provenance.lineage == ("middle", "leaf")


def test_one_typed_authority_per_component_is_enforced_by_value_shape():
    c = Component("x", "object", base_color=BaseColor.from_srgb("x", "#ffffff"))
    assert c.base_color is not None
    with pytest.raises(BaseColorError):
        adapt_legacy_base_color(c)


def test_typed_and_legacy_base_sources_are_rejected_as_contradictory():
    c = Component("x", "object", base_color=BaseColor.from_srgb("x", "#ffffff"))
    from visual_engine.components.common.meta import AppearanceLayer
    c.appearance.append(AppearanceLayer("legacy", {"base_color": "#ffffff"}))
    with pytest.raises(BaseColorError, match="both typed BASE authority"):
        resolve_base_color(RuntimeGraph.from_component(c), "x")


def test_multiple_legacy_base_sources_are_rejected():
    from visual_engine.components.common.meta import AppearanceLayer
    c = Component("x", "object")
    c.appearance.extend([
        AppearanceLayer("a", {"base_color": "#ffffff"}),
        AppearanceLayer("b", {"base_color": "#000000"}),
    ])
    with pytest.raises(BaseColorError, match="multiple legacy BASE authorities"):
        adapt_legacy_base_color(c)


def test_legacy_adapter_is_explicit_and_provenanced():
    from visual_engine.components.common.meta import AppearanceLayer
    c = Component("x", "object")
    c.appearance.append(AppearanceLayer("base", {"base_color": "#AaBbCc"}))
    color = adapt_legacy_base_color(c)
    assert color.source.kind is BaseColorSourceKind.AUTHORED
    assert color.source.source_id == "legacy:x:base"
    assert color.authored_representation.value == "#AaBbCc"


def test_malformed_authored_representation_is_rejected():
    with pytest.raises(BaseColorError):
        BaseColorAuthoredRepresentation("linear-srgb", "#ffffff")
    with pytest.raises(BaseColorError):
        BaseColorAuthoredRepresentation("srgb", "#fff")


def test_alpha_semantics_cannot_lie_about_alpha():
    from visual_engine.runtime.color_spaces import ColorRGBA
    with pytest.raises(BaseColorError, match="alpha_semantics"):
        BaseColor(
            ColorRGBA.from_hex("#ffffff80"),
            BaseColorAuthoredRepresentation("srgb", "#ffffff80"),
            BaseColorSource(BaseColorSourceKind.AUTHORED, "x", "x"),
            BaseColorProvenance("x", "x", "x", ("x",)),
            alpha_semantics=AlphaSemantics.OPAQUE,
        )


def test_generated_without_generator_provenance_is_rejected():
    from visual_engine.runtime.color_spaces import ColorRGBA
    with pytest.raises(BaseColorError, match="generator provenance"):
        BaseColor(
            ColorRGBA.from_hex("#ffffff"),
            None,
            BaseColorSource(BaseColorSourceKind.GENERATED, "gen:x", "x"),
            BaseColorProvenance("x", "x", "gen:x", ("x",)),
        )


def test_fingerprint_changes_for_appearance_but_not_geometry():
    root = Component("root", "object", base_color=BaseColor.from_srgb("root", "#112233"))
    child = Component("child", "object")
    root.add_child(child)
    graph = RuntimeGraph.from_component(root)
    before = base_color_resolution_fingerprint(graph, "child")
    child.geometry = GeometryContract(bounds=GeometryBounds(0, 0, 1, 1))
    graph2 = RuntimeGraph.from_component(root)
    after_geometry = base_color_resolution_fingerprint(graph2, "child")
    assert before == after_geometry


def test_unrelated_sibling_base_color_does_not_invalidate_target():
    root = Component("root", "object")
    a = Component("a", "object", base_color=BaseColor.from_srgb("a", "#111111"))
    b = Component("b", "object", base_color=BaseColor.from_srgb("b", "#222222"))
    root.add_child(a)
    root.add_child(b)
    graph = RuntimeGraph.from_component(root)
    before = base_color_resolution_fingerprint(graph, "a")
    b.base_color = BaseColor.from_srgb("b", "#333333")
    graph2 = RuntimeGraph.from_component(root)
    assert base_color_resolution_fingerprint(graph2, "a") == before


def test_local_wins_target_does_not_depend_on_ancestor_color():
    root = Component("root", "object", base_color=BaseColor.from_srgb("root", "#111111"))
    child = Component("child", "object", base_color=BaseColor.from_srgb("child", "#222222"))
    root.add_child(child)
    before = base_color_resolution_fingerprint(RuntimeGraph.from_component(root), "child")
    root.base_color = BaseColor.from_srgb("root", "#333333")
    after = base_color_resolution_fingerprint(RuntimeGraph.from_component(root), "child")
    assert before == after


def test_ancestor_change_invalidates_inherited_target():
    root = Component("root", "object", base_color=BaseColor.from_srgb("root", "#111111"))
    child = Component("child", "object")
    root.add_child(child)
    before = base_color_resolution_fingerprint(RuntimeGraph.from_component(root), "child")
    root.base_color = BaseColor.from_srgb("root", "#333333")
    after = base_color_resolution_fingerprint(RuntimeGraph.from_component(root), "child")
    assert before != after


def test_invalidation_explanation_is_targeted():
    root = Component("root", "object", base_color=BaseColor.from_srgb("root", "#111111"))
    child = Component("child", "object")
    sibling = Component("sibling", "object", base_color=BaseColor.from_srgb("sibling", "#222222"))
    root.add_child(child)
    root.add_child(sibling)
    graph = RuntimeGraph.from_component(root)
    assert base_color_invalidation(graph, "child", "root").affects_target
    assert not base_color_invalidation(graph, "child", "sibling").affects_target


def test_source_and_provenance_contradictions_are_rejected():
    from visual_engine.runtime.color_spaces import ColorRGBA
    with pytest.raises(BaseColorError, match="source and provenance source_id"):
        BaseColor(
            ColorRGBA.from_hex("#ffffff"),
            BaseColorAuthoredRepresentation("srgb", "#ffffff"),
            BaseColorSource(BaseColorSourceKind.AUTHORED, "source-a", "x"),
            BaseColorProvenance("x", "x", "source-b", ("x",)),
        )


def test_generated_color_cannot_claim_authored_representation():
    from visual_engine.runtime.color_spaces import ColorRGBA
    with pytest.raises(BaseColorError, match="cannot claim an authored representation"):
        BaseColor(
            ColorRGBA.from_hex("#ffffff"),
            BaseColorAuthoredRepresentation("srgb", "#ffffff"),
            BaseColorSource(BaseColorSourceKind.GENERATED, "gen:x", "x"),
            BaseColorProvenance("x", "x", "gen:x", ("x",), rule="generated-authority", generator_id="g", generator_version="1"),
        )


def test_inherited_for_rejects_blocked_authority():
    color = BaseColor.from_srgb("root", "#123456", inheritance=BaseColorInheritance(allow_children=False))
    with pytest.raises(BaseColorError, match="does not allow inheritance"):
        color.inherited_for("child", lineage=("root", "child"))


def test_provenance_lineage_must_end_at_target():
    from visual_engine.runtime.color_spaces import ColorRGBA
    with pytest.raises(BaseColorError, match="end at the target"):
        BaseColor(
            ColorRGBA.from_hex("#ffffff"),
            BaseColorAuthoredRepresentation("srgb", "#ffffff"),
            BaseColorSource(BaseColorSourceKind.AUTHORED, "x", "x"),
            BaseColorProvenance("target", "x", "x", ("x",)),
        )
