from __future__ import annotations

"""Renderer-neutral appearance boundary.

This module deliberately defines *what* an appearance resolver receives and
returns. It does not perform color mixing, lighting, material shading, or
renderer-specific drawing. Those systems can consume this stable envelope later.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Callable, TYPE_CHECKING
import math

from visual_engine.components.common.meta import AppearanceLayer
from visual_engine.components.common.visual_contract import ContourContract, MaterialContract

if TYPE_CHECKING:  # pragma: no cover
    from visual_engine.runtime.appearance_role_bridge import AppearanceRoleContribution


class AppearanceDomain(str, Enum):
    BASE = "base"
    MATERIAL = "material"
    STATE = "state"
    EFFECT = "effect"
    LIGHTING = "lighting"
    COLOR = "color"
    TRANSMISSION = "transmission"
    REFLECTION = "reflection"
    EMISSION = "emission"


class DomainContractError(ValueError):
    """Raised when an appearance contribution violates its domain contract."""


@dataclass(frozen=True, slots=True)
class DomainFieldContract:
    """Semantic contract for one field; this layer validates, never transforms."""

    name: str
    value_kind: str
    required: bool = False
    minimum: float | None = None
    maximum: float | None = None
    enum_values: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class DomainContract:
    """Closed vocabulary and type/range contract for one appearance domain."""

    domain: AppearanceDomain
    fields: tuple[DomainFieldContract, ...]
    allow_empty: bool = True

    @property
    def field_map(self) -> dict[str, DomainFieldContract]:
        return {field.name: field for field in self.fields}


_VALIDATED_DOMAINS = (
    AppearanceDomain.BASE,
    AppearanceDomain.MATERIAL,
    AppearanceDomain.COLOR,
    AppearanceDomain.LIGHTING,
    AppearanceDomain.TRANSMISSION,
    AppearanceDomain.REFLECTION,
    AppearanceDomain.EMISSION,
)

def _field(name: str, kind: str, *, required: bool = False, minimum: float | None = None, maximum: float | None = None, enum_values: tuple[str, ...] = ()) -> DomainFieldContract:
    return DomainFieldContract(name, kind, required, minimum, maximum, enum_values)


DOMAIN_CONTRACTS: Mapping[AppearanceDomain, DomainContract] = {
    AppearanceDomain.BASE: DomainContract(AppearanceDomain.BASE, (
        _field("base_color", "hex_color", required=True),
    )),
    AppearanceDomain.MATERIAL: DomainContract(AppearanceDomain.MATERIAL, (
        _field("name", "string"),
        _field("roughness", "unit"),
        _field("metallic", "unit"),
        _field("transmission", "unit"),
        _field("emission", "unit"),
    )),
    AppearanceDomain.COLOR: DomainContract(AppearanceDomain.COLOR, (
        # Legacy/compatibility vocabulary remains accepted at this generic
        # boundary, but V1.31's typed COLOR resolver consumes the explicit
        # canonical fields below and does not interpret the legacy modifiers.
        _field("base_color", "hex_color"),
        _field("pattern", "string"),
        _field("palette", "string_tuple"),
        _field("contrast", "finite"),
        _field("saturation", "finite"),
        _field("vibrance", "finite"),
        _field("lightness", "finite"),
        _field("temperature", "finite"),
        _field("color", "canonical_color"),
        _field("role", "string", enum_values=("primary", "secondary", "accent", "detail", "background", "custom")),
        _field("source", "string", enum_values=("base", "palette")),
        _field("authored_srgb", "hex_color"),
    )),
    AppearanceDomain.LIGHTING: DomainContract(AppearanceDomain.LIGHTING, (
        _field("color", "hex_color"),
        _field("intensity", "nonnegative"),
        _field("ambient_intensity", "nonnegative"),
        _field("key_intensity", "nonnegative"),
        _field("fill_intensity", "nonnegative"),
        _field("rim_intensity", "nonnegative"),
        _field("bounce_intensity", "nonnegative"),
        _field("direction", "vector"),
        _field("temperature_kelvin", "positive"),
    )),
    AppearanceDomain.TRANSMISSION: DomainContract(AppearanceDomain.TRANSMISSION, (
        _field("amount", "unit"),
        _field("ior", "positive", minimum=1.0),
        _field("thickness", "nonnegative"),
        _field("absorption_color", "hex_color"),
        _field("absorption_distance", "positive"),
    )),
    AppearanceDomain.REFLECTION: DomainContract(AppearanceDomain.REFLECTION, (
        _field("strength", "unit"),
        _field("roughness", "unit"),
        _field("color", "hex_color"),
        _field("ior", "positive", minimum=1.0),
    )),
    AppearanceDomain.EMISSION: DomainContract(AppearanceDomain.EMISSION, (
        _field("color", "hex_color"),
        _field("intensity", "nonnegative"),
        _field("temperature_kelvin", "positive"),
    )),
}


def _is_finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _validate_field(field: DomainFieldContract, value: Any) -> None:
    kind = field.value_kind
    if kind == "string":
        valid = isinstance(value, str) and bool(value)
    elif kind == "hex_color":
        valid = isinstance(value, str) and len(value) in (7, 9) and value.startswith("#")
        if valid:
            try:
                int(value[1:], 16)
            except ValueError:
                valid = False
    elif kind == "string_tuple":
        valid = isinstance(value, (tuple, list)) and all(isinstance(v, str) and bool(v) for v in value)
    elif kind == "canonical_color":
        from visual_engine.runtime.color_spaces import ColorRGBA
        valid = isinstance(value, ColorRGBA)
    elif kind in {"finite", "nonnegative", "positive", "unit"}:
        valid = _is_finite_number(value)
    elif kind == "vector":
        valid = isinstance(value, (tuple, list)) and 2 <= len(value) <= 3 and all(_is_finite_number(v) for v in value)
    else:
        raise DomainContractError(f"unsupported domain field kind: {kind}")
    if not valid:
        raise DomainContractError(f"invalid value for field '{field.name}' (expected {kind})")
    if _is_finite_number(value):
        number = float(value)
        if kind == "unit" and not 0.0 <= number <= 1.0:
            raise DomainContractError(f"field '{field.name}' must be in [0,1]")
        if kind == "nonnegative" and number < 0.0:
            raise DomainContractError(f"field '{field.name}' must be >= 0")
        if kind == "positive" and number <= 0.0:
            raise DomainContractError(f"field '{field.name}' must be > 0")
        if field.minimum is not None and number < field.minimum:
            raise DomainContractError(f"field '{field.name}' must be >= {field.minimum}")
        if field.maximum is not None and number > field.maximum:
            raise DomainContractError(f"field '{field.name}' must be <= {field.maximum}")
    if field.enum_values and value not in field.enum_values:
        raise DomainContractError(f"field '{field.name}' has unsupported value {value!r}")


def validate_appearance_contribution(contribution: "AppearanceContribution") -> None:
    """Validate a contribution against its declared domain, without interpretation."""
    contract = DOMAIN_CONTRACTS.get(contribution.domain)
    if contract is None:
        # STATE/EFFECT are control/resolution domains and have their own contracts.
        return
    values = dict(contribution.values)
    field_map = contract.field_map
    unknown = sorted(set(values) - set(field_map))
    if unknown:
        raise DomainContractError(
            f"domain '{contribution.domain.value}' does not declare fields: {', '.join(unknown)}"
        )
    missing = sorted(field.name for field in contract.fields if field.required and field.name not in values)
    if missing:
        raise DomainContractError(
            f"domain '{contribution.domain.value}' requires fields: {', '.join(missing)}"
        )
    if not values and not contract.allow_empty:
        raise DomainContractError(f"domain '{contribution.domain.value}' does not allow an empty contribution")
    for name, value in values.items():
        _validate_field(field_map[name], value)


def validate_appearance_contributions(contributions: tuple["AppearanceContribution", ...] | list["AppearanceContribution"]) -> None:
    """Validate every contribution; fail closed on the first semantic violation."""
    for contribution in contributions:
        validate_appearance_contribution(contribution)


@dataclass(frozen=True, slots=True)
class AppearanceContribution:
    """One explicitly typed appearance contribution.

    ``values`` remains semantic data at this boundary. No key is interpreted as
    a color operation unless a downstream resolver explicitly owns that domain.
    """

    contribution_id: str
    domain: AppearanceDomain
    source_id: str
    values: tuple[tuple[str, Any], ...] = ()
    opacity: float = 1.0

    def __post_init__(self) -> None:
        if not self.contribution_id or not self.source_id:
            raise ValueError("appearance contribution identifiers are required")
        if not 0.0 <= self.opacity <= 1.0:
            raise ValueError("appearance contribution opacity must be in [0,1]")
        keys = [key for key, _ in self.values]
        if any(not isinstance(key, str) or not key for key in keys):
            raise ValueError("appearance contribution keys must be non-empty strings")
        if len(keys) != len(set(keys)):
            raise ValueError("appearance contribution keys must be unique")
        object.__setattr__(self, "values", tuple(sorted(self.values, key=lambda item: item[0])))


@dataclass(frozen=True, slots=True)
class AppearanceResolutionInput:
    """Complete immutable input to an appearance resolver for one target."""

    target_id: str
    base_color: str
    contour: ContourContract
    material: MaterialContract
    opacity: float
    visibility: float
    active_states: tuple[str, ...] = ()
    appearance_layers: tuple[AppearanceLayer, ...] = ()
    contributions: tuple[AppearanceContribution, ...] = ()
    layer_resolution_digest: str = ""
    role_contribution: "AppearanceRoleContribution | None" = None

    def __post_init__(self) -> None:
        if not self.target_id:
            raise ValueError("appearance target_id must not be empty")
        if not isinstance(self.base_color, str) or len(self.base_color) not in (7, 9) or not self.base_color.startswith("#"):
            raise ValueError("base_color must be #RRGGBB or #RRGGBBAA")
        if not 0.0 <= self.opacity <= 1.0 or not 0.0 <= self.visibility <= 1.0:
            raise ValueError("appearance opacity/visibility must be in [0,1]")
        if any(not isinstance(value, str) or not value for value in self.active_states):
            raise ValueError("active state names must be non-empty strings")
        if tuple(sorted(set(self.active_states))) != self.active_states:
            raise ValueError("active_states must be canonicalized")
        if any(not isinstance(layer, AppearanceLayer) for layer in self.appearance_layers):
            raise ValueError("appearance_layers must contain AppearanceLayer instances")
        if any(not isinstance(item, AppearanceContribution) for item in self.contributions):
            raise ValueError("contributions must contain AppearanceContribution instances")
        if self.layer_resolution_digest and (len(self.layer_resolution_digest) != 64 or any(c not in "0123456789abcdef" for c in self.layer_resolution_digest.lower())):
            raise ValueError("layer_resolution_digest must be a SHA-256 hexadecimal digest")
        ids = [item.contribution_id for item in self.contributions]
        if len(ids) != len(set(ids)):
            raise ValueError("appearance contribution IDs must be unique")
        if self.role_contribution is not None:
            from visual_engine.runtime.appearance_role_bridge import AppearanceRoleContribution
            if not isinstance(self.role_contribution, AppearanceRoleContribution):
                raise ValueError("role_contribution must be AppearanceRoleContribution")
            if self.role_contribution.target_id != self.target_id:
                raise ValueError("role_contribution target does not match appearance target")
            if self.base_color != self.role_contribution.legacy_base_color:
                raise ValueError("legacy base_color contradicts typed role contribution")


@dataclass(frozen=True, slots=True)
class AppearanceResolutionResult:
    """Explicit output envelope; values are not yet shaded/rendered."""

    target_id: str
    base_color: str
    contour: ContourContract
    material: MaterialContract
    opacity: float
    visibility: float
    contributions: tuple[AppearanceContribution, ...]
    unresolved_domains: tuple[AppearanceDomain, ...]
    layer_resolution_digest: str = ""

    @property
    def effective_visibility(self) -> float:
        return self.visibility * self.opacity


def build_appearance_input(
    target_id: str,
    *,
    base_color: str,
    contour: ContourContract,
    material: MaterialContract,
    opacity: float,
    visibility: float,
    active_states: tuple[str, ...] = (),
    appearance_layers: tuple[AppearanceLayer, ...] = (),
    contributions: tuple[AppearanceContribution, ...] = (),
    layer_resolution_digest: str = "",
    role_contribution: "AppearanceRoleContribution | None" = None,
) -> AppearanceResolutionInput:
    """Construct the explicit appearance boundary without applying semantics."""
    return AppearanceResolutionInput(
        target_id=target_id,
        base_color=base_color,
        contour=contour,
        material=material,
        opacity=opacity,
        visibility=visibility,
        active_states=tuple(sorted(set(active_states))),
        appearance_layers=appearance_layers,
        contributions=contributions,
        layer_resolution_digest=layer_resolution_digest,
        role_contribution=role_contribution,
    )


def resolve_appearance_contract(data: AppearanceResolutionInput) -> AppearanceResolutionResult:
    """Freeze currently-known appearance inputs for downstream domain resolvers.

    Only opacity/visibility are already defined generic composition quantities.
    Base color, material and appearance-layer payloads are intentionally preserved
    rather than guessed into lighting/color operations.
    """
    validate_appearance_contributions(data.contributions)
    return AppearanceResolutionResult(
        target_id=data.target_id,
        base_color=data.base_color.lower(),
        contour=data.contour,
        material=data.material,
        opacity=data.opacity,
        visibility=data.visibility,
        contributions=data.contributions,
        layer_resolution_digest=data.layer_resolution_digest,
        unresolved_domains=(
            AppearanceDomain.LIGHTING,
            AppearanceDomain.COLOR,
            AppearanceDomain.TRANSMISSION,
            AppearanceDomain.REFLECTION,
            AppearanceDomain.EMISSION,
        ),
    )


def build_component_appearance_input(
    component,
    *,
    base_color: str,
    contour: ContourContract,
    material: MaterialContract,
    opacity: float,
    visibility: float,
    active_states: tuple[str, ...] = (),
    effects=(),
    bindings=(),
    policies=(),
) -> tuple[AppearanceResolutionInput, object]:
    """Resolve explicit local appearance layers, then enter the appearance contract.

    This is intentionally a bridge rather than a new inheritance engine. Parent
    appearance is not traversed; state activation and effect selection arrive as
    already-resolved inputs. The second return value is the layer-resolution audit
    record, including its dependency digest.
    """
    from visual_engine.runtime.appearance_layers import resolve_appearance_layers

    layer_result = resolve_appearance_layers(
        component,
        active_states=active_states,
        effects=effects,
        bindings=bindings,
        policies=policies,
    )
    data = build_appearance_input(
        component.id,
        base_color=base_color,
        contour=contour,
        material=material,
        opacity=opacity,
        visibility=visibility,
        active_states=tuple(active_states),
        appearance_layers=tuple(component.appearance),
        contributions=layer_result.contributions,
        layer_resolution_digest=layer_result.dependency_digest,
    )
    return data, layer_result
