from __future__ import annotations

"""Generic geometry-to-geometry spatial placement resolution.

This module resolves *relationships*, not object categories.  A source geometry
can be positioned relative to an arbitrary target geometry using explicit anchors,
relative dimensions and (optionally) a geometric coverage target.  No eye/hand/
hair/glasses vocabulary is embedded here.
"""

import math

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.runtime.placement_coverage import CoverageIntent, resolve_coverage_scale
from visual_engine.runtime.region_geometry import geometry_to_region

_EPS = 1e-9


from visual_engine.runtime.placement_contract import (
    AnchorReference, DimensionConstraint, PlacementDepthRelation, PlacementIntent,
    PlacementScaleMode, PlacementSolution,
)


def _anchor(geometry: GeometryContract, reference: AnchorReference) -> tuple[float, float, float]:
    try:
        return tuple(float(v) for v in geometry.anchors[reference.name])  # type: ignore[return-value]
    except KeyError as exc:
        raise KeyError(f"geometry does not define anchor {reference.name!r}") from exc


def _bounds_size(geometry: GeometryContract) -> tuple[float, float]:
    width = geometry.bounds.max_x - geometry.bounds.min_x
    height = geometry.bounds.max_y - geometry.bounds.min_y
    if width <= _EPS or height <= _EPS:
        region = geometry_to_region(geometry)
        if region.is_empty:
            raise ValueError("geometry has no positive-area bounds")
        min_x, min_y, max_x, max_y = region.bounds
        width, height = max_x - min_x, max_y - min_y
    if width <= _EPS or height <= _EPS:
        raise ValueError("geometry must have positive width and height")
    return float(width), float(height)


def _target_point(target: GeometryContract, reference: AnchorReference) -> tuple[float, float, float]:
    return _anchor(target, reference)



def resolve_placement(source: GeometryContract, target: GeometryContract, intent: PlacementIntent) -> PlacementSolution:
    """Resolve a source geometry relative to a target geometry.

    The solver only understands geometry, anchors, dimensions and explicit
    relationship intent. It never inspects component/object names to infer how
    the source should behave.
    """
    if source.coordinate_frame != target.coordinate_frame:
        raise ValueError("source and target geometries must share a coordinate frame")
    source_anchor = _anchor(source, intent.source_anchor)
    target_anchor = _target_point(target, intent.target_anchor)

    scale_x = scale_y = 1.0
    diagnostics: dict[str, float | str] = {"mode": intent.scale_mode.value}

    if intent.dimension is not None:
        sw, sh = _bounds_size(source)
        tw, th = _bounds_size(target)
        candidates_x = [intent.dimension.width_ratio * tw / sw] if intent.dimension.width_ratio is not None else []
        candidates_y = [intent.dimension.height_ratio * th / sh] if intent.dimension.height_ratio is not None else []
        if intent.scale_mode is PlacementScaleMode.UNIFORM:
            candidates = candidates_x + candidates_y
            if len(candidates) > 1 and abs(candidates[0] - candidates[1]) > 1e-9 * max(1.0, abs(candidates[0]), abs(candidates[1])):
                raise ValueError("uniform dimension constraints are inconsistent")
            if candidates:
                scale_x = scale_y = candidates[0]
        else:
            if candidates_x:
                scale_x = candidates_x[0]
            if candidates_y:
                scale_y = candidates_y[0]

    resolved_fraction = None
    coverage_error = None
    if intent.coverage is not None:
        source_region = geometry_to_region(source)
        target_region = geometry_to_region(target)
        scale_x, resolved_fraction, iterations = resolve_coverage_scale(
            source_region, target_region, source_anchor, target_anchor,
            intent.coverage, intent.rotation_deg, intent.offset_x, intent.offset_y,
        )
        scale_y = scale_x
        coverage_error = abs(resolved_fraction - intent.coverage.target_fraction)
        diagnostics["coverage_iterations"] = float(iterations)
        diagnostics["coverage_target"] = float(intent.coverage.target_fraction)

    angle = math.radians(intent.rotation_deg)
    ca, sa = math.cos(angle), math.sin(angle)
    # The public transform is represented as p' = R(S(p)) + translation.
    # Therefore the source anchor must be rotated/scaled before the translation
    # is solved. This remains correct for arbitrary anchor coordinates and rotation.
    anchor_x = ca * (scale_x * source_anchor[0]) - sa * (scale_y * source_anchor[1])
    anchor_y = sa * (scale_x * source_anchor[0]) + ca * (scale_y * source_anchor[1])
    tx = target_anchor[0] + intent.offset_x - anchor_x
    ty = target_anchor[1] + intent.offset_y - anchor_y
    diagnostics["target_width"] = _bounds_size(target)[0]
    diagnostics["target_height"] = _bounds_size(target)[1]

    return PlacementSolution(
        source_id=intent.source_id,
        target_id=intent.target_id,
        translation=(tx, ty),
        rotation_deg=intent.rotation_deg,
        scale_x=scale_x,
        scale_y=scale_y,
        z_offset=intent.depth_offset,
        source_anchor=source_anchor,
        target_anchor=target_anchor,
        resolved_target_fraction=resolved_fraction,
        coverage_error=coverage_error,
        diagnostics=diagnostics,
    )


def resolve_placed_geometry(
    geometry: GeometryContract,
    solution: PlacementSolution,
    *,
    coordinate_frame: str | None = None,
) -> GeometryContract:
    """Materialize a placement solution as renderer-independent source geometry.

    This applies only the relation-local affine placement. Scene/camera transforms
    remain owned by ``geometry_transform`` so placement and composition cannot be
    accidentally conflated.
    """
    from visual_engine.runtime.geometry_contract_transform import transform_geometry_contract
    frame = coordinate_frame or geometry.coordinate_frame
    return transform_geometry_contract(geometry, solution.matrix, z_offset=solution.z_offset, coordinate_frame=frame)
