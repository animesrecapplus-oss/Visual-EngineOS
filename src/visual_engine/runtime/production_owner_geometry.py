from __future__ import annotations

"""Extract one production geometry owner without resolving or rendering it."""

from visual_engine.components.common.geometry_contract import GeometryContract


def extract_production_owner_geometry(
    geometry: GeometryContract, owner_id: str
) -> tuple[GeometryContract, float]:
    """Return the owner's camera-space geometry and one authored depth layer.

    The implementation intentionally preserves the former production helper's
    selection/rebasing semantics. It does not resolve appearance, visibility,
    occlusion, cache identity, or renderer output.
    """
    if not isinstance(geometry, GeometryContract):
        raise TypeError("production owner geometry requires a GeometryContract")
    if not isinstance(owner_id, str) or not owner_id:
        raise ValueError("owner_id must be a non-empty string")

    surfaces = [
        surface for surface in geometry.surfaces
        if str(surface.data.get("source_component_id", "")) == owner_id
    ]
    if not surfaces:
        raise ValueError(f"production visibility owner {owner_id!r} has no surfaced geometry")

    depth_values = {
        int(surface.data["depth_layer"])
        for surface in surfaces
        if "depth_layer" in surface.data
    }
    if not depth_values:
        raise ValueError(f"production visibility owner {owner_id!r} has no explicit depth_layer")
    if len(depth_values) != 1:
        raise ValueError(f"production visibility owner {owner_id!r} has inconsistent depth layers")

    selected_paths: list = []
    selected_primitives: list = []
    selected_surfaces = []
    path_map: dict[int, int] = {}
    for surface in surfaces:
        raw_path = surface.data.get("path_index")
        data = dict(surface.data)
        if raw_path is not None:
            source_index = int(raw_path)
            if source_index < 0 or source_index >= len(geometry.paths):
                raise ValueError(f"surface {surface.name!r} references an invalid path index")
            if source_index not in path_map:
                path_map[source_index] = len(selected_paths)
                selected_paths.append(geometry.paths[source_index])
            data["path_index"] = path_map[source_index]
        selected_surfaces.append(type(surface)(surface.name, data))

    for primitive in geometry.primitives:
        if str(primitive.data.get("component_id", "")) == owner_id:
            selected_primitives.append(primitive)

    return GeometryContract(
        coordinate_frame=geometry.coordinate_frame,
        bounds=geometry.bounds,
        primitives=tuple(selected_primitives),
        paths=tuple(selected_paths),
        surfaces=tuple(selected_surfaces),
        local_z=geometry.local_z,
    ), float(next(iter(depth_values)))
