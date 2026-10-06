from __future__ import annotations

import pytest

from visual_engine.components.common.geometry_contract import GeometryBounds, GeometryContract, GeometryPrimitive
from visual_engine.components.common.meta import Component, Relation
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.placement import PlacementDepthRelation
from visual_engine.runtime.region_maps import SemanticRegionProviderRegistry, generic_region_provider, resolve_region_map
from visual_engine.runtime.spatial_relationships import (
    compile_relation_placement,
    resolve_graph_placements,
    resolve_relation_placement,
)


def _rect(component_id: str, kind: str, x0: float, y0: float, x1: float, y1: float, *, center: tuple[float, float, float]):
    return Component(
        component_id,
        kind,
        anchors={"center": __import__("visual_engine.model", fromlist=["Anchor"]).Anchor("center", *center)},
        geometry=GeometryContract(
            coordinate_frame="scene",
            bounds=GeometryBounds(x0, y0, x1, y1),
            primitives=(GeometryPrimitive("polygon", {"semantic_region": "surface", "points": ((x0,y0),(x1,y0),(x1,y1),(x0,y1))}),),
            anchors={"center": center},
        ),
    )


def _graph_with_relation(relation: Relation) -> RuntimeGraph:
    root = Component("root", "Root")
    source = _rect("source", "Source", 0, 0, 2, 2, center=(1, 1, 0))
    target = _rect("target", "Target", 10, 10, 30, 30, center=(20, 20, 0))
    source.relations.append(relation)
    root.add_child(source)
    root.add_child(target)
    return RuntimeGraph.from_component(root)


def test_relation_compiles_only_explicit_placement_metadata():
    relation = Relation("source", "ATTACHMENT", "target", metadata={
        "placement": {
            "source_anchor": "center",
            "target_anchor": "center",
            "width_ratio": 0.5,
            "height_ratio": 0.5,
            "depth_relation": "behind",
            "depth_offset": -2,
        }
    })
    spec = compile_relation_placement(relation)
    assert spec is not None
    assert spec.intent.source_id == "source"
    assert spec.intent.target_id == "target"
    assert spec.intent.depth_relation is PlacementDepthRelation.BEHIND
    assert spec.intent.depth_offset == -2


def test_relation_without_placement_is_not_synthesized():
    assert compile_relation_placement(Relation("source", "ATTACHMENT", "target")) is None


def test_relation_placement_targets_explicit_semantic_region_and_preserves_component_anchor():
    relation = Relation("source", "ATTACHMENT", "target", metadata={
        "placement": {
            "source_anchor": "center",
            "target_anchor": "center",
            "target_region_id": "target:region:surface",
            "target_anchor_scope": "component",
            "width_ratio": 0.5,
            "height_ratio": 0.5,
        }
    })
    graph = _graph_with_relation(relation)
    registry = SemanticRegionProviderRegistry()
    registry.register(generic_region_provider(kinds=("Target",)))
    target_map = resolve_region_map(graph, "target", graph.get("target").component.geometry, registry, target="local").region_map
    result = resolve_relation_placement(
        graph, relation,
        graph.get("source").component.geometry,
        graph.get("target").component.geometry,
        target_region_map=target_map,
    )
    assert result.target_region_id == "target:region:surface"
    assert result.solution.target_anchor == (20, 20, 0)
    assert result.solution.scale_x == pytest.approx(5.0)
    assert result.solution.scale_y == pytest.approx(5.0)


def test_region_anchor_scope_requires_explicit_region_anchor():
    relation = Relation("source", "ATTACHMENT", "target", metadata={
        "placement": {
            "source_anchor": "center",
            "target_anchor": "center",
            "target_region_id": "target:region:surface",
            "target_anchor_scope": "region",
            "width_ratio": 0.5,
        }
    })
    graph = _graph_with_relation(relation)
    registry = SemanticRegionProviderRegistry()
    registry.register(generic_region_provider(kinds=("Target",)))
    target_map = resolve_region_map(graph, "target", graph.get("target").component.geometry, registry, target="local").region_map
    with pytest.raises(KeyError, match="does not define anchor 'center'"):
        resolve_relation_placement(
            graph, relation,
            graph.get("source").component.geometry,
            graph.get("target").component.geometry,
            target_region_map=target_map,
        )


def test_graph_resolver_only_resolves_explicit_placement_relations_in_deterministic_order():
    first = Relation("source", "ATTACHMENT", "target", metadata={
        "placement": {"source_anchor": "center", "target_anchor": "center", "width_ratio": 0.5}
    })
    graph = _graph_with_relation(first)
    geometries = {node_id: node.component.geometry for node_id, node in graph.nodes.items()}
    results = resolve_graph_placements(graph, geometries)
    assert len(results) == 1
    assert results[0].source_id == "source"
    assert results[0].target_id == "target"


def test_unknown_placement_metadata_key_fails_closed():
    relation = Relation("source", "ATTACHMENT", "target", metadata={
        "placement": {"source_anchor": "center", "target_anchor": "center", "widht_ratio": 0.5}
    })
    with pytest.raises(ValueError, match="unknown placement metadata keys"):
        compile_relation_placement(relation)


def test_relation_compiles_explicit_hard_constraints():
    relation = Relation(
        "source", "ATTACHMENT", "target",
        metadata={
            "placement": {
                "source_anchor": "origin",
                "target_anchor": "origin",
                "constraints": {"containment": {"tolerance": 1e-8}},
            }
        },
    )
    spec = compile_relation_placement(relation)
    assert spec is not None
    assert spec.constraints is not None
    assert spec.constraints.containment.tolerance == 1e-8


def test_relation_unknown_constraint_is_rejected():
    relation = Relation(
        "source", "ATTACHMENT", "target",
        metadata={
            "placement": {
                "source_anchor": "origin",
                "target_anchor": "origin",
                "constraints": {"magic": {}},
            }
        },
    )
    with pytest.raises(ValueError, match="unknown placement constraint keys"):
        compile_relation_placement(relation)


def test_relation_placement_enforces_declared_hard_constraint():
    relation = Relation(
        "source", "ATTACHMENT", "target",
        metadata={
            "placement": {
                "source_anchor": "center",
                "target_anchor": "center",
                "constraints": {"non_penetration": {}},
            }
        },
    )
    graph = _graph_with_relation(relation)
    source_geometry = graph.get("source").component.geometry
    target_geometry = graph.get("target").component.geometry
    with pytest.raises(ValueError, match="non_penetration"):
        resolve_relation_placement(graph, relation, source_geometry, target_geometry)
