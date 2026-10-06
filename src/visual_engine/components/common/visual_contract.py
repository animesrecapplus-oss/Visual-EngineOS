from __future__ import annotations

from dataclasses import dataclass, field
import hashlib
import json
import math
from typing import Any


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def _hex(value: str, name: str) -> str:
    if not isinstance(value, str) or len(value) not in (7, 9) or not value.startswith("#"):
        raise ValueError(f"{name} must be #RRGGBB or #RRGGBBAA")
    try:
        int(value[1:], 16)
    except ValueError as exc:
        raise ValueError(f"{name} must be hexadecimal") from exc
    return value.lower()


def _unit(value: float, name: str) -> float:
    value = _finite(value, name)
    if not 0.0 <= value <= 1.0:
        raise ValueError(f"{name} must be in [0,1]")
    return value


@dataclass(frozen=True, slots=True)
class LocalTransform:
    """2D component-local transform. Parent composition is handled by runtime."""

    x: float = 0.0
    y: float = 0.0
    rotation_deg: float = 0.0
    scale_x: float = 1.0
    scale_y: float = 1.0
    z: float = 0.0

    def __post_init__(self) -> None:
        for name, value in (("x", self.x), ("y", self.y), ("rotation_deg", self.rotation_deg), ("z", self.z)):
            _finite(value, name)
        if not math.isfinite(self.scale_x) or not math.isfinite(self.scale_y):
            raise ValueError("scale must be finite")
        if self.scale_x == 0 or self.scale_y == 0:
            raise ValueError("scale components must be non-zero")

    def matrix(self) -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]:
        angle = math.radians(self.rotation_deg)
        c, s = math.cos(angle), math.sin(angle)
        return (
            (c * self.scale_x, -s * self.scale_y, self.x),
            (s * self.scale_x, c * self.scale_y, self.y),
            (0.0, 0.0, 1.0),
        )


@dataclass(frozen=True, slots=True)
class ContourContract:
    color: str = "#000000"
    width: float = 1.0
    opacity: float = 1.0
    style: str = "solid"
    cap: str = "round"
    join: str = "round"

    def __post_init__(self) -> None:
        _hex(self.color, "contour color")
        if self.width < 0 or not math.isfinite(self.width):
            raise ValueError("contour width must be finite and >= 0")
        _unit(self.opacity, "contour opacity")
        if self.style not in {"solid", "dashed", "dotted", "none"}:
            raise ValueError("unsupported contour style")
        if self.cap not in {"butt", "round", "square"}:
            raise ValueError("unsupported contour cap")
        if self.join not in {"miter", "round", "bevel"}:
            raise ValueError("unsupported contour join")


@dataclass(frozen=True, slots=True)
class MaterialContract:
    name: str = "default"
    roughness: float = 1.0
    metallic: float = 0.0
    transmission: float = 0.0
    emission: float = 0.0

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("material name must not be empty")
        for name, value in (("roughness", self.roughness), ("metallic", self.metallic), ("transmission", self.transmission), ("emission", self.emission)):
            _unit(value, name)




@dataclass(frozen=True, slots=True)
class ContourOverride:
    """Optional field-level override. None means inherit the resolved parent value."""

    color: str | None = None
    width: float | None = None
    opacity: float | None = None
    style: str | None = None
    cap: str | None = None
    join: str | None = None

    def __post_init__(self) -> None:
        if self.color is not None:
            _hex(self.color, "contour override color")
        if self.width is not None and (self.width < 0 or not math.isfinite(self.width)):
            raise ValueError("contour override width must be finite and >= 0")
        if self.opacity is not None:
            _unit(self.opacity, "contour override opacity")
        if self.style is not None and self.style not in {"solid", "dashed", "dotted", "none"}:
            raise ValueError("unsupported contour override style")
        if self.cap is not None and self.cap not in {"butt", "round", "square"}:
            raise ValueError("unsupported contour override cap")
        if self.join is not None and self.join not in {"miter", "round", "bevel"}:
            raise ValueError("unsupported contour override join")


@dataclass(frozen=True, slots=True)
class MaterialOverride:
    """Optional field-level material override. None means inherit."""

    name: str | None = None
    roughness: float | None = None
    metallic: float | None = None
    transmission: float | None = None
    emission: float | None = None

    def __post_init__(self) -> None:
        if self.name is not None and not self.name:
            raise ValueError("material override name must not be empty")
        for name, value in (("roughness", self.roughness), ("metallic", self.metallic), ("transmission", self.transmission), ("emission", self.emission)):
            if value is not None:
                _unit(value, f"material override {name}")


@dataclass(frozen=True, slots=True)
class VisualOverrides:
    """Explicit child requests applied to an already resolved parent context.

    A None field is an explicit *inherit* instruction. This object exists beside
    VisualContract so legacy components with fully specified VisualContract values
    remain backwards compatible.
    """

    fill_color: str | None = None
    contour: ContourOverride | None = None
    material: MaterialOverride | None = None
    opacity: float | None = None
    visibility: float | None = None

    def __post_init__(self) -> None:
        if self.fill_color is not None:
            _hex(self.fill_color, "fill override color")
        if self.opacity is not None:
            _unit(self.opacity, "opacity override")
        if self.visibility is not None:
            _unit(self.visibility, "visibility override")


@dataclass(frozen=True, slots=True)
class VisualContract:
    """Generic appearance contract shared by every renderable component."""

    fill_color: str = "#ffffff"
    contour: ContourContract = field(default_factory=ContourContract)
    material: MaterialContract = field(default_factory=MaterialContract)
    opacity: float = 1.0
    visibility: float = 1.0

    def __post_init__(self) -> None:
        _hex(self.fill_color, "fill color")
        _unit(self.opacity, "opacity")
        _unit(self.visibility, "visibility")


@dataclass(frozen=True, slots=True)
class ResolvedVisualContract:
    """Immutable hot-path contract after inheritance/effects have been resolved."""

    world_transform: tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]
    world_z: float
    visibility: float
    opacity: float
    effective_fill_color: str
    effective_contour: ContourContract
    material: MaterialContract
    shadow_alpha: float = 0.0
    shadow_color: str = "#000000"
    occluded_by: tuple[str, ...] = ()
    active_states: tuple[str, ...] = ()
    applied_effect_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        _finite(self.world_z, "world_z")
        _unit(self.visibility, "visibility")
        _unit(self.opacity, "opacity")
        _unit(self.shadow_alpha, "shadow_alpha")
        _hex(self.effective_fill_color, "effective fill color")
        _hex(self.shadow_color, "shadow color")
        if any(not isinstance(v, str) or not v for v in self.applied_effect_ids):
            raise ValueError("applied_effect_ids entries must be non-empty strings")
        if len(set(self.applied_effect_ids)) != len(self.applied_effect_ids):
            raise ValueError("applied_effect_ids must be unique")

    @property
    def effective_visibility(self) -> float:
        return self.visibility * self.opacity


def canonical_contract_payload(contract: VisualContract, transform: LocalTransform) -> dict[str, Any]:
    return {
        "transform": {
            "x": transform.x,
            "y": transform.y,
            "rotation_deg": transform.rotation_deg,
            "scale_x": transform.scale_x,
            "scale_y": transform.scale_y,
            "z": transform.z,
        },
        "visual": {
            "fill_color": contract.fill_color,
            "contour": {
                "color": contract.contour.color,
                "width": contract.contour.width,
                "opacity": contract.contour.opacity,
                "style": contract.contour.style,
                "cap": contract.contour.cap,
                "join": contract.contour.join,
            },
            "material": {
                "name": contract.material.name,
                "roughness": contract.material.roughness,
                "metallic": contract.material.metallic,
                "transmission": contract.material.transmission,
                "emission": contract.material.emission,
            },
            "opacity": contract.opacity,
            "visibility": contract.visibility,
        },
    }


def contract_hash(contract: VisualContract, transform: LocalTransform) -> str:
    """Stable identity for deterministic cache keys; no Python hash()."""
    payload = canonical_contract_payload(contract, transform)
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def identity_matrix() -> tuple[tuple[float, float, float], tuple[float, float, float], tuple[float, float, float]]:
    return ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))


def compose_matrices(a, b):
    """Compose homogeneous 2D transforms without decomposition/recomposition."""
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)) for i in range(3))


def transform_point(matrix, x: float, y: float) -> tuple[float, float]:
    return (
        matrix[0][0] * x + matrix[0][1] * y + matrix[0][2],
        matrix[1][0] * x + matrix[1][1] * y + matrix[1][2],
    )


def matrix_is_finite(matrix) -> bool:
    return all(math.isfinite(float(v)) for row in matrix for v in row)


def matrix_determinant(matrix) -> float:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
