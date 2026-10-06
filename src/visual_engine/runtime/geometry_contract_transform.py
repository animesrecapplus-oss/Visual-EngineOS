from __future__ import annotations

import math

from visual_engine.components.common.geometry_contract import (
    GeometryBounds,
    GeometryContract,
    GeometryMask,
    GeometryPath,
    GeometryPrimitive,
    GeometrySurface,
)
from visual_engine.components.common.visual_contract import (
    matrix_determinant,
    matrix_is_finite,
    transform_point,
)

Matrix3 = tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]

# This module owns contract-coordinate transformation; it deliberately depends on
# geometry/transform primitives only, so renderer and scene orchestration stay outside.


def _transform_bounds(bounds: GeometryBounds, matrix: Matrix3) -> GeometryBounds:
    corners = (
        transform_point(matrix, bounds.min_x, bounds.min_y),
        transform_point(matrix, bounds.min_x, bounds.max_y),
        transform_point(matrix, bounds.max_x, bounds.min_y),
        transform_point(matrix, bounds.max_x, bounds.max_y),
    )
    xs = [p[0] for p in corners]
    ys = [p[1] for p in corners]
    return GeometryBounds(min(xs), min(ys), max(xs), max(ys))


def _transform_path(path: GeometryPath, matrix: Matrix3) -> GeometryPath:
    transformed = []
    for command, values in path.commands:
        if command in {"M", "L"}:
            x, y = transform_point(matrix, values[0], values[1])
            transformed.append((command, (x, y)))
        elif command == "C":
            p1 = transform_point(matrix, values[0], values[1])
            p2 = transform_point(matrix, values[2], values[3])
            p3 = transform_point(matrix, values[4], values[5])
            transformed.append((command, (*p1, *p2, *p3)))
        elif command == "Q":
            p1 = transform_point(matrix, values[0], values[1])
            p2 = transform_point(matrix, values[2], values[3])
            transformed.append((command, (*p1, *p2)))
        else:
            transformed.append((command, ()))
    return GeometryPath(tuple(transformed))


def _ellipse_axes(matrix: Matrix3, rx: float, ry: float, rotation_deg: float = 0.0) -> tuple[float, float, float]:
    """Map an axis-aligned ellipse through an arbitrary affine 2D transform.

    Returns semi-axis lengths and world orientation. This is the singular-value
    decomposition of A * R(rotation) * diag(rx, ry), specialized to 2x2 so the
    geometry layer does not depend on NumPy.
    """
    angle = math.radians(rotation_deg)
    ca, sa = math.cos(angle), math.sin(angle)
    # B = linear(matrix) * R(angle) * diag(rx, ry)
    a00 = matrix[0][0] * ca + matrix[0][1] * sa
    a01 = (-matrix[0][0] * sa + matrix[0][1] * ca)
    a10 = matrix[1][0] * ca + matrix[1][1] * sa
    a11 = (-matrix[1][0] * sa + matrix[1][1] * ca)
    b00, b01 = a00 * rx, a01 * ry
    b10, b11 = a10 * rx, a11 * ry
    c00 = b00 * b00 + b01 * b01
    c01 = b00 * b10 + b01 * b11
    c11 = b10 * b10 + b11 * b11
    trace = c00 + c11
    det = max(0.0, c00 * c11 - c01 * c01)
    disc = max(0.0, trace * trace - 4.0 * det)
    lam1 = max(0.0, 0.5 * (trace + math.sqrt(disc)))
    lam2 = max(0.0, 0.5 * (trace - math.sqrt(disc)))
    major = math.sqrt(lam1)
    minor = math.sqrt(lam2)
    if major <= 1e-15:
        return 0.0, 0.0, 0.0
    if abs(c01) > 1e-12 or abs(c00 - lam1) > 1e-12:
        vx, vy = c01, lam1 - c00
        norm = math.hypot(vx, vy)
        if norm > 1e-15:
            vx, vy = vx / norm, vy / norm
            orientation = math.degrees(math.atan2(vy, vx))
        else:
            orientation = 0.0
    else:
        orientation = 0.0 if c00 >= c11 else 90.0
    return major, minor, orientation


def _transform_primitive(primitive: GeometryPrimitive, matrix: Matrix3) -> GeometryPrimitive:
    data = dict(primitive.data)
    kind = primitive.kind
    if kind in {"ellipse", "circle"} and "cx" in data and "cy" in data:
        cx, cy = transform_point(matrix, float(data["cx"]), float(data["cy"]))
        if "r" in data:
            rx = ry = float(data["r"])
        elif "rx" in data and "ry" in data:
            rx, ry = float(data["rx"]), float(data["ry"])
        else:
            raise ValueError(f"{kind} primitive requires r or rx/ry")
        major, minor, orientation = _ellipse_axes(matrix, rx, ry, float(data.get("rotation_deg", 0.0)))
        data.pop("r", None)
        data["cx"], data["cy"] = cx, cy
        data["rx"], data["ry"] = major, minor
        data["rotation_deg"] = orientation
        if data.get("shape") == "circle" and abs(major - minor) > 1e-9 * max(1.0, major, minor):
            data["shape"] = "ellipse"
        return GeometryPrimitive("ellipse", data)
    if kind == "point" and "x" in data and "y" in data:
        data["x"], data["y"] = transform_point(matrix, float(data["x"]), float(data["y"]))
        return GeometryPrimitive(kind, data)
    if kind == "line" and all(key in data for key in ("x1", "y1", "x2", "y2")):
        data["x1"], data["y1"] = transform_point(matrix, float(data["x1"]), float(data["y1"]))
        data["x2"], data["y2"] = transform_point(matrix, float(data["x2"]), float(data["y2"]))
        return GeometryPrimitive(kind, data)
    if kind == "polygon" and "points" in data:
        points = []
        for point in data["points"]:
            if len(point) != 2:
                raise ValueError("polygon points must contain x/y pairs")
            points.append(transform_point(matrix, float(point[0]), float(point[1])))
        data["points"] = tuple(points)
        return GeometryPrimitive(kind, data)
    # Metadata-only primitives are not transformed. Geometric primitives must use
    # an explicit supported representation; silently translating unknown payloads
    # would make occlusion/intersection data unreliable later.
    if kind not in {"metadata"}:
        raise ValueError(f"unsupported transformable geometry primitive kind: {kind!r}")
    return GeometryPrimitive(kind, data)


def transform_geometry_contract(
    geometry: GeometryContract,
    matrix: Matrix3,
    *,
    z_offset: float = 0.0,
    coordinate_frame: str = "world",
) -> GeometryContract:
    """Transform every geometric field from one 2D frame into another.

    Paths, known geometric primitives, anchors and bounds are transformed. Surface
    and mask semantic metadata is preserved. Unknown geometric primitive encodings
    fail closed instead of being silently corrupted.
    """
    if not matrix_is_finite(matrix):
        raise ValueError("transform matrix must be finite")
    if abs(matrix_determinant(matrix)) <= 1e-15:
        raise ValueError("geometry transform must be invertible")
    primitives = tuple(_transform_primitive(p, matrix) for p in geometry.primitives)
    paths = tuple(_transform_path(p, matrix) for p in geometry.paths)
    anchors = {}
    for name, point in geometry.anchors.items():
        x, y = transform_point(matrix, point[0], point[1])
        anchors[name] = (x, y, float(point[2]) + float(z_offset))
    return GeometryContract(
        coordinate_frame=coordinate_frame,
        bounds=_transform_bounds(geometry.bounds, matrix),
        primitives=primitives,
        paths=paths,
        surfaces=tuple(GeometrySurface(s.name, dict(s.data)) for s in geometry.surfaces),
        masks=tuple(GeometryMask(m.name, m.operation, dict(m.data)) for m in geometry.masks),
        anchors=anchors,
        local_z=geometry.local_z + z_offset,
    )

