from __future__ import annotations

"""Compile graph relations into explicit spatial placement intents.

This layer is deliberately declarative. A relation may declare a ``placement``
payload, which is validated and compiled into :class:`PlacementIntent`.
Component/object categories are never inspected here.
"""

from dataclasses import dataclass
import math
from typing import Any, Mapping

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.meta import Relation
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.placement_coverage import CoverageIntent
from visual_engine.runtime.placement import (
    AnchorReference,
    DimensionConstraint,
    PlacementDepthRelation,
    PlacementIntent,
    PlacementScaleMode,
    PlacementSolution,
    resolve_placement,
)
from visual_engine.runtime.semantic_regions import RegionMap, SemanticRegion
from visual_engine.runtime.placement_constraints import PlacementConstraintSet, resolve_constrained_placement

_ALLOWED_RELATIONS = frozenset({"SPATIAL", "ATTACHMENT", "GEOMETRIC", "CONTACT", "OCCLUSION"})
_ALLOWED_KEYS = frozenset({
    "source_anchor", "target_anchor", "target_region_id", "target_anchor_scope",
    "rotation_deg", "offset_x", "offset_y", "scale_mode", "width_ratio", "height_ratio",
    "coverage", "coverage_tolerance", "coverage_max_iterations", "depth_relation", "depth_offset",
    "constraints",
})


def _finite_number(value: Any, name: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"placement.{name} must be numeric")
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"placement.{name} must be numeric") from exc
    if not math.isfinite(result):
        raise ValueError(f"placement.{name} must be finite")
    return result


def _required_string(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value:
        raise ValueError(f"placement.{key} must be a non-empty string")
    return value


@dataclass(frozen=True, slots=True)
class RelationPlacementSpec:
    """Validated placement declaration extracted from one graph relation."""

    relation: Relation
    intent: PlacementIntent
    target_region_id: str | None = None
    target_anchor_scope: str = "component"
    constraints: "PlacementConstraintSet | None" = None

    def __post_init__(self) -> None:
        if self.target_anchor_scope not in {"component", "region"}:
            raise ValueError("target_anchor_scope must be component or region")
        if self.target_region_id is not None and not self.target_region_id:
            raise ValueError("target_region_id must be non-empty")


@dataclass(frozen=True, slots=True)
class RelationPlacementResolution:
    relation_id: str
    source_id: str
    target_id: str
    target_region_id: str | None
    solution: PlacementSolution

    def __post_init__(self) -> None:
        if not self.relation_id or not self.source_id or not self.target_id:
            raise ValueError("relation placement resolution identity is required")
        if self.solution.source_id != self.source_id or self.solution.target_id != self.target_id:
            raise ValueError("placement solution endpoints do not match relation")


def _relation_id(relation: Relation) -> str:
    # Relation objects do not currently have a persisted ID. The tuple is stable
    # for the current graph contract and rejects ambiguous duplicate declarations.
    from visual_engine.runtime.versioning import stable_digest
    return stable_digest({
        "source_id": relation.source_id,
        "relation_type": relation.relation_type,
        "target_id": relation.target_id,
        "metadata": relation.metadata,
    })


def compile_relation_placement(relation: Relation) -> RelationPlacementSpec | None:
    """Compile one relation's explicit ``placement`` metadata.

    Relations without a placement declaration return ``None``. Malformed
    declarations fail closed. Unknown placement keys are rejected to prevent
    silent typos from changing geometry semantics.
    """
    raw = relation.metadata.get("placement")
    if raw is None:
        return None
    if relation.relation_type not in _ALLOWED_RELATIONS:
        raise ValueError(f"relation type {relation.relation_type!r} cannot declare placement")
    if not isinstance(raw, Mapping):
        raise ValueError("relation placement metadata must be a mapping")
    unknown = set(raw) - _ALLOWED_KEYS
    if unknown:
        raise ValueError(f"unknown placement metadata keys: {sorted(unknown)}")

    source_anchor = AnchorReference(_required_string(raw, "source_anchor"))
    target_anchor = AnchorReference(_required_string(raw, "target_anchor"))
    scale_mode = PlacementScaleMode(str(raw.get("scale_mode", PlacementScaleMode.UNIFORM.value)))
    depth_relation = PlacementDepthRelation(str(raw.get("depth_relation", PlacementDepthRelation.FRONT.value)))

    dimension = None
    if "width_ratio" in raw or "height_ratio" in raw:
        dimension = DimensionConstraint(
            width_ratio=_finite_number(raw["width_ratio"], "width_ratio") if "width_ratio" in raw else None,
            height_ratio=_finite_number(raw["height_ratio"], "height_ratio") if "height_ratio" in raw else None,
        )

    coverage = None
    if "coverage" in raw:
        coverage = CoverageIntent(
            target_fraction=_finite_number(raw["coverage"], "coverage"),
            tolerance=_finite_number(raw.get("coverage_tolerance", 1e-3), "coverage_tolerance"),
            max_iterations=int(raw.get("coverage_max_iterations", 48)),
        )

    target_region_id = raw.get("target_region_id")
    if target_region_id is not None and (not isinstance(target_region_id, str) or not target_region_id):
        raise ValueError("placement.target_region_id must be a non-empty string")
    target_anchor_scope = str(raw.get("target_anchor_scope", "component"))

    constraints = None
    if "constraints" in raw:
        from visual_engine.runtime.placement_constraints import (
            ClearanceConstraint, ContainmentConstraint, NonPenetrationConstraint, PlacementConstraintSet,
        )
        raw_constraints = raw["constraints"]
        if not isinstance(raw_constraints, Mapping):
            raise ValueError("placement.constraints must be a mapping")
        allowed_constraints = {"containment", "clearance", "non_penetration"}
        unknown_constraints = set(raw_constraints) - allowed_constraints
        if unknown_constraints:
            raise ValueError(f"unknown placement constraint keys: {sorted(unknown_constraints)}")
        containment = None
        if "containment" in raw_constraints:
            value = raw_constraints["containment"]
            if not isinstance(value, Mapping):
                raise ValueError("placement.constraints.containment must be a mapping")
            containment = ContainmentConstraint(tolerance=_finite_number(value.get("tolerance", 1e-9), "constraints.containment.tolerance"))
        clearance = None
        if "clearance" in raw_constraints:
            value = raw_constraints["clearance"]
            if not isinstance(value, Mapping):
                raise ValueError("placement.constraints.clearance must be a mapping")
            if "minimum_distance" not in value:
                raise ValueError("placement.constraints.clearance.minimum_distance is required")
            clearance = ClearanceConstraint(
                minimum_distance=_finite_number(value["minimum_distance"], "constraints.clearance.minimum_distance"),
                tolerance=_finite_number(value.get("tolerance", 1e-9), "constraints.clearance.tolerance"),
            )
        non_penetration = None
        if "non_penetration" in raw_constraints:
            value = raw_constraints["non_penetration"]
            if not isinstance(value, Mapping):
                raise ValueError("placement.constraints.non_penetration must be a mapping")
            non_penetration = NonPenetrationConstraint(tolerance=_finite_number(value.get("tolerance", 1e-9), "constraints.non_penetration.tolerance"))
        constraints = PlacementConstraintSet(
            containment=containment, clearance=clearance, non_penetration=non_penetration,
        )

    intent = PlacementIntent(
        source_id=relation.source_id,
        target_id=relation.target_id,
        source_anchor=source_anchor,
        target_anchor=target_anchor,
        rotation_deg=_finite_number(raw.get("rotation_deg", 0.0), "rotation_deg"),
        offset_x=_finite_number(raw.get("offset_x", 0.0), "offset_x"),
        offset_y=_finite_number(raw.get("offset_y", 0.0), "offset_y"),
        scale_mode=scale_mode,
        dimension=dimension,
        coverage=coverage,
        depth_relation=depth_relation,
        depth_offset=_finite_number(raw.get("depth_offset", 1.0 if depth_relation is PlacementDepthRelation.FRONT else (-1.0 if depth_relation is PlacementDepthRelation.BEHIND else 0.0)), "depth_offset"),
    )
    return RelationPlacementSpec(relation, intent, target_region_id, target_anchor_scope, constraints)


def _target_geometry(
    target_geometry: GeometryContract,
    target_region_map: RegionMap | None,
    region_id: str | None,
    anchor_name: str,
    anchor_scope: str,
) -> GeometryContract:
    if region_id is None:
        return target_geometry
    if target_region_map is None:
        raise ValueError("target_region_map is required when target_region_id is declared")
    region = target_region_map.get(region_id)
    if anchor_scope == "region":
        if anchor_name not in region.geometry.anchors:
            raise KeyError(f"target region {region_id!r} does not define anchor {anchor_name!r}")
        return region.geometry
    if anchor_scope == "component":
        # The target component anchor remains a valid placement reference while
        # the region supplies the geometry to be dimensioned/covered. Copy only
        # that explicit anchor; never infer a center or other anchor.
        if anchor_name not in target_geometry.anchors:
            raise KeyError(f"target component does not define anchor {anchor_name!r}")
        anchors = dict(region.geometry.anchors)
        anchors[anchor_name] = target_geometry.anchors[anchor_name]
        return GeometryContract(
            coordinate_frame=region.geometry.coordinate_frame,
            bounds=region.geometry.bounds,
            primitives=region.geometry.primitives,
            paths=region.geometry.paths,
            surfaces=region.geometry.surfaces,
            masks=region.geometry.masks,
            anchors=anchors,
            local_z=region.geometry.local_z,
        )
    raise ValueError("target_anchor_scope must be component or region")


def resolve_relation_placement(
    graph: RuntimeGraph,
    relation: Relation,
    source_geometry: GeometryContract,
    target_geometry: GeometryContract,
    *,
    target_region_map: RegionMap | None = None,
) -> RelationPlacementResolution:
    """Resolve one graph relation into a placement solution.

    The supplied geometries must already be in a common coordinate frame. This
    function deliberately does not invent camera/scene transforms; callers use
    the established geometry transform pipeline before entering this solver.
    """
    if relation.source_id not in graph.nodes or relation.target_id not in graph.nodes:
        raise ValueError("relation endpoints are not present in graph")
    spec = compile_relation_placement(relation)
    if spec is None:
        raise ValueError("relation has no placement declaration")
    target = _target_geometry(
        target_geometry, target_region_map, spec.target_region_id,
        spec.intent.target_anchor.name, spec.target_anchor_scope,
    )
    if spec.constraints is not None:
        solution = resolve_constrained_placement(source_geometry, target, spec.intent, spec.constraints).solution
    else:
        solution = resolve_placement(source_geometry, target, spec.intent)
    return RelationPlacementResolution(
        relation_id=_relation_id(relation),
        source_id=relation.source_id,
        target_id=relation.target_id,
        target_region_id=spec.target_region_id,
        solution=solution,
    )


def resolve_graph_placements(
    graph: RuntimeGraph,
    geometries: Mapping[str, GeometryContract],
    *,
    region_maps: Mapping[str, RegionMap] | None = None,
) -> tuple[RelationPlacementResolution, ...]:
    """Resolve all explicit placement relations deterministically.

    Every referenced endpoint must have a geometry. No placement relation is
    synthesized for ordinary relations without explicit ``metadata.placement``.
    """
    region_maps = region_maps or {}
    results: list[RelationPlacementResolution] = []
    for relation in sorted(graph.relations, key=lambda r: (r.source_id, r.target_id, r.relation_type, _relation_id(r))):
        if "placement" not in relation.metadata:
            continue
        try:
            source_geometry = geometries[relation.source_id]
            target_geometry = geometries[relation.target_id]
        except KeyError as exc:
            raise KeyError(f"missing geometry for relation endpoint {exc.args[0]!r}") from exc
        results.append(resolve_relation_placement(
            graph, relation, source_geometry, target_geometry,
            target_region_map=region_maps.get(relation.target_id),
        ))
    return tuple(results)


def resolve_relation_constrained_placement(
    graph: RuntimeGraph,
    relation: Relation,
    source_geometry: GeometryContract,
    target_geometry: GeometryContract,
    *,
    target_region_map: RegionMap | None = None,
    constraints=None,
):
    """Resolve an explicit relation with additional hard geometric predicates."""
    if relation.source_id not in graph.nodes or relation.target_id not in graph.nodes:
        raise ValueError("relation endpoints are not present in graph")
    spec = compile_relation_placement(relation)
    if spec is None:
        raise ValueError("relation has no placement declaration")
    if constraints is None:
        constraints = spec.constraints or PlacementConstraintSet()
    if not isinstance(constraints, PlacementConstraintSet):
        raise TypeError("constraints must be a PlacementConstraintSet")
    target = _target_geometry(
        target_geometry, target_region_map, spec.target_region_id,
        spec.intent.target_anchor.name, spec.target_anchor_scope,
    )
    solved = resolve_constrained_placement(source_geometry, target, spec.intent, constraints)
    return RelationPlacementResolution(
        relation_id=_relation_id(relation),
        source_id=relation.source_id,
        target_id=relation.target_id,
        target_region_id=spec.target_region_id,
        solution=solved.solution,
    )
