from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math
from typing import Any, Mapping


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _finite_tree(value: Any, path: str = "value", _active: set[int] | None = None) -> Any:
    """Normalize nested geometry metadata without key coercion or recursion traps."""
    active = _active if _active is not None else set()
    if isinstance(value, bool) or value is None or isinstance(value, str):
        return value
    if isinstance(value, (int, float)):
        return _finite(value, path)
    marker = id(value)
    if marker in active:
        raise ValueError(f"cyclic geometry payload at {path}")
    if isinstance(value, (list, tuple)):
        active.add(marker)
        try:
            return tuple(_finite_tree(v, f"{path}[{i}]", active) for i, v in enumerate(value))
        finally:
            active.remove(marker)
    if isinstance(value, Mapping):
        active.add(marker)
        try:
            result = {}
            for key, item in value.items():
                if not isinstance(key, str):
                    raise TypeError(f"geometry metadata keys must be strings at {path}")
                result[key] = _finite_tree(item, f"{path}.{key}", active)
            return result
        finally:
            active.remove(marker)
    raise TypeError(f"Unsupported geometry payload type at {path}: {type(value).__name__}")


@dataclass(frozen=True, slots=True)
class GeometryBounds:
    """Axis-aligned local bounds. They are renderer-independent."""

    min_x: float = 0.0
    min_y: float = 0.0
    max_x: float = 0.0
    max_y: float = 0.0

    def __post_init__(self) -> None:
        for name, value in (("min_x", self.min_x), ("min_y", self.min_y), ("max_x", self.max_x), ("max_y", self.max_y)):
            _finite(value, name)
        if self.max_x < self.min_x or self.max_y < self.min_y:
            raise ValueError("Geometry bounds max values must be >= min values")


@dataclass(frozen=True, slots=True)
class GeometryPrimitive:
    """Generic geometry primitive. `data` contains only deterministic scalar/sequence data."""

    kind: str
    data: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.kind:
            raise ValueError("Geometry primitive kind must not be empty")
        object.__setattr__(self, "data", _finite_tree(dict(self.data)))


@dataclass(frozen=True, slots=True)
class GeometryPath:
    """Renderer-neutral path command sequence (M/L/C/Q/Z or future commands)."""

    commands: tuple[tuple[str, tuple[float, ...]], ...] = ()

    def __post_init__(self) -> None:
        normalized: list[tuple[str, tuple[float, ...]]] = []
        arity = {"M": 2, "L": 2, "C": 6, "Q": 4, "Z": 0}
        for command, values in self.commands:
            if not command:
                raise ValueError("Geometry path command must not be empty")
            code = command.upper()
            if code not in arity:
                raise ValueError(f"unsupported geometry path command: {code}")
            vals = tuple(_finite(v, f"path {code}") for v in values)
            if len(vals) != arity[code]:
                raise ValueError(f"path {code} expects {arity[code]} values, got {len(vals)}")
            normalized.append((code, vals))
        object.__setattr__(self, "commands", tuple(normalized))


@dataclass(frozen=True, slots=True)
class GeometrySurface:
    """Optional surface metadata used later by occlusion/material systems."""

    name: str
    data: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("Geometry surface name must not be empty")
        object.__setattr__(self, "data", _finite_tree(dict(self.data)))


@dataclass(frozen=True, slots=True)
class GeometryMask:
    """Named local mask reference; actual mask realization belongs to renderers/occlusion."""

    name: str
    operation: str = "clip"
    data: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.name or not self.operation:
            raise ValueError("Geometry mask requires name and operation")
        if self.operation not in {"clip", "subtract", "intersect", "union"}:
            raise ValueError("Unsupported geometry mask operation")
        object.__setattr__(self, "data", _finite_tree(dict(self.data)))


@dataclass(frozen=True, slots=True)
class GeometryContract:
    """Generic renderer-neutral geometry contract shared by every component."""

    coordinate_frame: str = "local"
    bounds: GeometryBounds = field(default_factory=GeometryBounds)
    primitives: tuple[GeometryPrimitive, ...] = ()
    paths: tuple[GeometryPath, ...] = ()
    surfaces: tuple[GeometrySurface, ...] = ()
    masks: tuple[GeometryMask, ...] = ()
    anchors: Mapping[str, tuple[float, float, float]] = field(default_factory=dict)
    local_z: float = 0.0

    def __post_init__(self) -> None:
        if not self.coordinate_frame:
            raise ValueError("coordinate_frame must not be empty")
        _finite(self.local_z, "local_z")
        normalized: dict[str, tuple[float, float, float]] = {}
        for name, point in self.anchors.items():
            if not name or len(point) != 3:
                raise ValueError("Geometry anchor requires a name and 3 coordinates")
            normalized[name] = tuple(_finite(v, f"anchor {name}") for v in point)
        object.__setattr__(self, "anchors", normalized)


def canonical_geometry_payload(geometry: GeometryContract) -> dict[str, Any]:
    return {
        "coordinate_frame": geometry.coordinate_frame,
        "bounds": {
            "min_x": geometry.bounds.min_x,
            "min_y": geometry.bounds.min_y,
            "max_x": geometry.bounds.max_x,
            "max_y": geometry.bounds.max_y,
        },
        "primitives": [{"kind": p.kind, "data": p.data} for p in geometry.primitives],
        "paths": [{"commands": [[cmd, list(values)] for cmd, values in p.commands]} for p in geometry.paths],
        "surfaces": [{"name": s.name, "data": s.data} for s in geometry.surfaces],
        "masks": [{"name": m.name, "operation": m.operation, "data": m.data} for m in geometry.masks],
        "anchors": {k: list(v) for k, v in sorted(geometry.anchors.items())},
        "local_z": geometry.local_z,
    }


def geometry_hash(geometry: GeometryContract) -> str:
    """Stable SHA-256 identity for geometry; never Python's process-randomized hash()."""
    encoded = json.dumps(canonical_geometry_payload(geometry), sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()
