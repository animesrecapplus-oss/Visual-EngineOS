from __future__ import annotations

from dataclasses import replace
from typing import Iterable, Mapping

from .geometry_contract import GeometryBounds, GeometryContract, GeometryPath, GeometryPrimitive, GeometrySurface


def _bounds_for_contracts(contracts: Iterable[GeometryContract]) -> GeometryBounds:
    values = tuple(contracts)
    if not values:
        return GeometryBounds()
    return GeometryBounds(
        min(c.bounds.min_x for c in values),
        min(c.bounds.min_y for c in values),
        max(c.bounds.max_x for c in values),
        max(c.bounds.max_y for c in values),
    )


def merge_geometry_contracts(
    contracts: Mapping[str, GeometryContract],
    *,
    coordinate_frame: str = "parent",
) -> GeometryContract:
    """Deterministically merge already parent-local geometry contracts.

    This utility deliberately does not invent transforms. A caller must first solve
    each child's local-to-parent placement. That keeps transform semantics explicit
    and prevents a composite generator from silently applying the wrong coordinate
    frame.
    """
    ordered = tuple(sorted(contracts.items(), key=lambda item: item[0]))
    geometries = tuple(geometry for _, geometry in ordered)
    primitives: list[GeometryPrimitive] = []
    paths: list[GeometryPath] = []
    surfaces: list[GeometrySurface] = []
    anchors: dict[str, tuple[float, float, float]] = {}
    local_z = 0.0

    for component_id, geometry in ordered:
        path_offset = len(paths)
        for primitive in geometry.primitives:
            data = dict(primitive.data)
            # Preserve an existing leaf owner when a nested composite is merged.
            # The parent component is still recorded separately by the surface layer.
            data.setdefault("component_id", component_id)
            primitives.append(GeometryPrimitive(primitive.kind, data))
        paths.extend(geometry.paths)
        for surface in geometry.surfaces:
            data = dict(surface.data)
            local_path_index = data.get("path_index")
            if local_path_index is not None:
                data["path_index"] = int(local_path_index) + path_offset
            data.setdefault("source_component_id", str(data.get("component_id", component_id)))
            data["component_id"] = component_id
            surfaces.append(GeometrySurface(f"{component_id}:{surface.name}", data))
        for name, point in geometry.anchors.items():
            key = f"{component_id}:{name}"
            anchors[key] = point
        local_z = max(local_z, geometry.local_z)

    return GeometryContract(
        coordinate_frame=coordinate_frame,
        bounds=_bounds_for_contracts(geometries),
        primitives=tuple(primitives),
        paths=tuple(paths),
        surfaces=tuple(surfaces),
        anchors=anchors,
        local_z=local_z,
    )
