from __future__ import annotations

"""Immutable contracts for generic spatial placement resolution."""

from dataclasses import dataclass, field
from enum import Enum
import math
from typing import Mapping

from visual_engine.runtime.placement_coverage import CoverageIntent

_EPS = 1e-9


class PlacementScaleMode(str, Enum):
    UNIFORM = "uniform"
    NON_UNIFORM = "non_uniform"


class PlacementDepthRelation(str, Enum):
    FRONT = "front"
    BEHIND = "behind"
    COPLANAR = "coplanar"


@dataclass(frozen=True, slots=True)
class AnchorReference:
    """Named anchor in a geometry contract."""
    name: str

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("anchor name must not be empty")


@dataclass(frozen=True, slots=True)
class DimensionConstraint:
    """Positive source-to-target dimension ratios; None leaves an axis free."""
    width_ratio: float | None = None
    height_ratio: float | None = None

    def __post_init__(self) -> None:
        for name, value in (("width_ratio", self.width_ratio), ("height_ratio", self.height_ratio)):
            if value is not None and (not math.isfinite(value) or value <= 0):
                raise ValueError(f"{name} must be finite and > 0")


@dataclass(frozen=True, slots=True)
class PlacementIntent:
    """Declarative spatial relationship; it contains no geometry-solving code."""
    source_id: str
    target_id: str
    source_anchor: AnchorReference
    target_anchor: AnchorReference
    rotation_deg: float = 0.0
    offset_x: float = 0.0
    offset_y: float = 0.0
    scale_mode: PlacementScaleMode = PlacementScaleMode.UNIFORM
    dimension: DimensionConstraint | None = None
    coverage: CoverageIntent | None = None
    depth_relation: PlacementDepthRelation = PlacementDepthRelation.FRONT
    depth_offset: float = 1.0

    def __post_init__(self) -> None:
        if not self.source_id or not self.target_id:
            raise ValueError("source_id and target_id are required")
        for name, value in (("rotation_deg", self.rotation_deg), ("offset_x", self.offset_x), ("offset_y", self.offset_y), ("depth_offset", self.depth_offset)):
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.depth_relation is PlacementDepthRelation.FRONT and self.depth_offset <= 0:
            raise ValueError("front depth_offset must be > 0")
        if self.depth_relation is PlacementDepthRelation.BEHIND and self.depth_offset >= 0:
            raise ValueError("behind depth_offset must be < 0")
        if self.depth_relation is PlacementDepthRelation.COPLANAR and abs(self.depth_offset) > _EPS:
            raise ValueError("coplanar depth_offset must be zero")
        if self.scale_mode is PlacementScaleMode.NON_UNIFORM and self.coverage is not None:
            raise ValueError("coverage solving requires uniform scaling")
        if self.dimension is not None and self.coverage is not None:
            raise ValueError("dimension and coverage constraints are mutually exclusive")


@dataclass(frozen=True, slots=True)
class PlacementSolution:
    """Immutable solver result and its local affine-transform contract."""
    source_id: str
    target_id: str
    translation: tuple[float, float]
    rotation_deg: float
    scale_x: float
    scale_y: float
    z_offset: float
    source_anchor: tuple[float, float, float]
    target_anchor: tuple[float, float, float]
    resolved_target_fraction: float | None = None
    coverage_error: float | None = None
    diagnostics: Mapping[str, float | str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.source_id or not self.target_id:
            raise ValueError("placement solution identity is required")
        for name, value in (("rotation_deg", self.rotation_deg), ("scale_x", self.scale_x), ("scale_y", self.scale_y), ("z_offset", self.z_offset)):
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.scale_x <= 0 or self.scale_y <= 0:
            raise ValueError("placement scales must be > 0")
        if len(self.translation) != 2 or not all(math.isfinite(v) for v in self.translation):
            raise ValueError("translation must contain finite x/y")
        if self.resolved_target_fraction is not None and not 0 <= self.resolved_target_fraction <= 1:
            raise ValueError("resolved_target_fraction must be in [0,1]")
        if self.coverage_error is not None and self.coverage_error < 0:
            raise ValueError("coverage_error must be >= 0")
        object.__setattr__(self, "diagnostics", dict(sorted((self.diagnostics or {}).items())))

    @property
    def matrix(self) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]:
        angle = math.radians(self.rotation_deg)
        ca, sa = math.cos(angle), math.sin(angle)
        return ((ca * self.scale_x, -sa * self.scale_y, self.translation[0]),
                (sa * self.scale_x, ca * self.scale_y, self.translation[1]), (0.0, 0.0, 1.0))

    def transform_point(self, x: float, y: float) -> tuple[float, float]:
        if not math.isfinite(x) or not math.isfinite(y):
            raise ValueError("point coordinates must be finite")
        matrix = self.matrix
        return (matrix[0][0] * x + matrix[0][1] * y + matrix[0][2],
                matrix[1][0] * x + matrix[1][1] * y + matrix[1][2])
