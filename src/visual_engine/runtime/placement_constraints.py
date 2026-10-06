from __future__ import annotations

"""Hard-constraint validation for generic spatial placement.

Constraint value contracts live in ``placement_constraints_contract``. This
module remains the compatibility/resolution owner and performs no soft
optimization: a violated explicit constraint fails closed.
"""

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.runtime.placement import PlacementIntent, PlacementSolution, resolve_placement
from visual_engine.runtime.placement_constraints_contract import (
    ClearanceConstraint,
    ConstraintCheck,
    ConstraintStatus,
    ConstrainedPlacementSolution,
    ContainmentConstraint,
    NonPenetrationConstraint,
    PlacementConstraintSet,
)
from visual_engine.runtime.region_geometry import geometry_to_region


def _placed_region(source: GeometryContract, solution: PlacementSolution):
    """Return the source footprint after the exact resolved affine transform."""
    from visual_engine.runtime.placement import resolve_placed_geometry
    placed_geometry = resolve_placed_geometry(source, solution)
    return geometry_to_region(placed_geometry)


def validate_placement_constraints(
    source: GeometryContract,
    target: GeometryContract,
    solution: PlacementSolution,
    constraints: PlacementConstraintSet,
) -> tuple[ConstraintCheck, ...]:
    """Evaluate explicit hard constraints without modifying the solution."""
    checks: list[ConstraintCheck] = []
    placed = _placed_region(source, solution)
    target_region = geometry_to_region(target)

    if constraints.containment is not None:
        if placed.is_empty or target_region.is_empty:
            raise ValueError("containment requires positive-area source and target regions")
        outside = placed.difference(target_region).area
        tolerance = constraints.containment.tolerance
        status = ConstraintStatus.SATISFIED if outside <= tolerance else ConstraintStatus.VIOLATED
        checks.append(ConstraintCheck("containment", status, float(outside), float(tolerance),
                                      "source is contained in target" if status is ConstraintStatus.SATISFIED
                                      else "source exceeds target boundary"))

    if constraints.clearance is not None:
        if placed.is_empty or target_region.is_empty:
            raise ValueError("clearance requires positive-area source and target regions")
        distance = float(placed.distance(target_region))
        minimum = constraints.clearance.minimum_distance
        tolerance = constraints.clearance.tolerance
        status = ConstraintStatus.SATISFIED if distance + tolerance >= minimum else ConstraintStatus.VIOLATED
        checks.append(ConstraintCheck("clearance", status, distance, minimum,
                                      "minimum clearance satisfied" if status is ConstraintStatus.SATISFIED
                                      else "minimum clearance violated"))

    if constraints.non_penetration is not None:
        if placed.is_empty or target_region.is_empty:
            raise ValueError("non-penetration requires positive-area source and target regions")
        overlap = float(placed.intersection(target_region).area)
        tolerance = constraints.non_penetration.tolerance
        status = ConstraintStatus.SATISFIED if overlap <= tolerance else ConstraintStatus.VIOLATED
        checks.append(ConstraintCheck("non_penetration", status, overlap, tolerance,
                                      "no area penetration" if status is ConstraintStatus.SATISFIED
                                      else "source penetrates target"))

    return tuple(checks)


def resolve_constrained_placement(
    source: GeometryContract,
    target: GeometryContract,
    intent: PlacementIntent,
    constraints: PlacementConstraintSet,
) -> ConstrainedPlacementSolution:
    """Resolve placement, then enforce explicit hard geometric predicates."""
    solution = resolve_placement(source, target, intent)
    checks = validate_placement_constraints(source, target, solution, constraints)
    violated = [c for c in checks if c.status is ConstraintStatus.VIOLATED]
    if violated:
        detail = "; ".join(f"{c.name}: {c.message}" for c in violated)
        raise ValueError(f"placement constraints unsatisfied: {detail}")
    return ConstrainedPlacementSolution(solution, checks)
