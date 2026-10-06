from __future__ import annotations

"""Renderer-independent conversion between GeometryContract and planar regions."""

from dataclasses import dataclass
import math
from typing import Iterable, Mapping

from shapely import geometry as sg
from shapely import ops as so

from visual_engine.components.common.geometry_contract import GeometryContract, GeometryPrimitive

_EPS = 1e-9


@dataclass(frozen=True, slots=True)
class BooleanPolygon:
    """Immutable polygon contract with optional interior rings."""

    exterior: tuple[tuple[float, float], ...]
    holes: tuple[tuple[tuple[float, float], ...], ...] = ()

    def __post_init__(self) -> None:
        if len(self.exterior) < 3:
            raise ValueError("BooleanPolygon exterior requires at least 3 points")
        if any(len(h) < 3 for h in self.holes):
            raise ValueError("BooleanPolygon holes require at least 3 points")


@dataclass(frozen=True, slots=True)
class RegionGeometry:
    """Boolean-resolved planar region represented as polygons and holes."""

    polygons: tuple[BooleanPolygon, ...] = ()

    @property
    def area(self) -> float:
        total = sum(_ring_area(p.exterior) - sum(_ring_area(h) for h in p.holes) for p in self.polygons)
        return max(0.0, total)


def _ring_area(points: Iterable[tuple[float, float]]) -> float:
    pts = tuple(points)
    return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                    for i in range(len(pts))) * 0.5)


def _clean_polygon(geom: sg.base.BaseGeometry) -> sg.base.BaseGeometry:
    if geom.is_empty:
        return geom
    fixed = geom.buffer(0)
    return fixed if not fixed.is_empty else geom

def _ellipse_polygon(data: Mapping[str, object], segments: int = 128) -> sg.Polygon:
    cx, cy = float(data["cx"]), float(data["cy"])
    if "r" in data:
        rx = ry = float(data["r"])
    else:
        rx, ry = float(data.get("rx", 0.0)), float(data.get("ry", 0.0))
    if rx < 0 or ry < 0:
        raise ValueError("ellipse radii must be non-negative")
    rotation = math.radians(float(data.get("rotation_deg", 0.0)))
    c, s = math.cos(rotation), math.sin(rotation)
    count = max(16, int(segments))
    points = []
    for i in range(count):
        t = 2.0 * math.pi * i / count
        x, y = rx * math.cos(t), ry * math.sin(t)
        points.append((cx + x * c - y * s, cy + x * s + y * c))
    return sg.Polygon(points)

# Fixed subdivision keeps coverage/attribution deterministic across renderer implementations.
def _path_points(path, *, curve_segments: int = 32) -> tuple[tuple[float, float], ...]:
    """Flatten one closed M/L/C/Q path deterministically for planar booleans."""
    if not path.commands or path.commands[0][0] != "M" or path.commands[-1][0] != "Z":
        raise ValueError("visibility path region requires a closed path beginning with M and ending with Z")
    points = [(float(path.commands[0][1][0]), float(path.commands[0][1][1]))]
    current = start = points[0]
    for command, values in path.commands[1:-1]:
        if command in {"M", "L"}:
            current = (float(values[0]), float(values[1]))
            points.append(current)
        elif command == "Q":
            p0, p1, p2 = current, (float(values[0]), float(values[1])), (float(values[2]), float(values[3]))
            count = max(4, curve_segments // 2)
            for i in range(1, count + 1):
                t, u = i / count, 1.0 - i / count
                points.append((u*u*p0[0] + 2*u*t*p1[0] + t*t*p2[0], u*u*p0[1] + 2*u*t*p1[1] + t*t*p2[1]))
            current = p2
        elif command == "C":
            p0 = current
            p1, p2 = (float(values[0]), float(values[1])), (float(values[2]), float(values[3]))
            p3 = (float(values[4]), float(values[5]))
            count = max(8, curve_segments)
            for i in range(1, count + 1):
                t, u = i / count, 1.0 - i / count
                points.append((u**3*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t**3*p3[0],
                               u**3*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t**3*p3[1]))
            current = p3
        else:
            raise ValueError(f"unsupported path command for visibility region: {command!r}")
    if math.dist(current, start) > _EPS:
        points.append(start)
    return tuple(points)

def path_to_region(path, *, curve_segments: int = 32) -> sg.base.BaseGeometry:
    """Convert one closed GeometryPath into a robust filled planar region."""
    points = _path_points(path, curve_segments=curve_segments)
    return sg.GeometryCollection() if len(points) < 4 else _clean_polygon(sg.Polygon(points))


def primitive_to_region(primitive: GeometryPrimitive, *, ellipse_segments: int = 128) -> sg.base.BaseGeometry:
    """Convert one supported area primitive into a robust planar region."""
    data, kind = primitive.data, primitive.kind
    if kind == "polygon":
        points = tuple((float(x), float(y)) for x, y in data.get("points", ()))
        return sg.GeometryCollection() if len(points) < 3 else _clean_polygon(sg.Polygon(points))
    if kind in {"ellipse", "circle"}:
        return _clean_polygon(_ellipse_polygon(data, ellipse_segments))
    raise ValueError(f"primitive kind {kind!r} cannot define an area region")


def geometry_to_region(geometry: GeometryContract, *, ellipse_segments: int = 128) -> sg.base.BaseGeometry:
    """Union explicit area primitives; renderer-only paths are never inferred."""
    shapes = [primitive_to_region(p, ellipse_segments=ellipse_segments) for p in geometry.primitives]
    shapes = [s for s in shapes if not s.is_empty and s.area > _EPS]
    return sg.GeometryCollection() if not shapes else _clean_polygon(so.unary_union(shapes))

def _ring_tuple(coords) -> tuple[tuple[float, float], ...]:
    pts = [(float(x), float(y)) for x, y in coords]
    if len(pts) > 1 and pts[0] == pts[-1]:
        pts.pop()
    return tuple(pts)


def region_to_contract(region: sg.base.BaseGeometry, *, coordinate_frame: str = "scene") -> RegionGeometry:
    """Convert a GEOS planar result back to an immutable renderer-neutral contract."""
    region = _clean_polygon(region)
    if region.is_empty:
        return RegionGeometry()
    geoms = region.geoms if region.geom_type == "MultiPolygon" else (region,)
    polygons = []
    for poly in geoms:
        if poly.geom_type != "Polygon" or poly.area <= _EPS:
            continue
        holes = tuple(_ring_tuple(r.coords) for r in poly.interiors)
        polygons.append(BooleanPolygon(_ring_tuple(poly.exterior.coords), holes))
    polygons.sort(key=lambda p: (-_ring_area(p.exterior), p.exterior))
    return RegionGeometry(tuple(polygons))
