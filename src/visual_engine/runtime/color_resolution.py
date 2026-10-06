from __future__ import annotations

"""Typed COLOR-domain resolution without mixing, grading or lighting.

V1.31 is intentionally the smallest real COLOR consumer.  It projects only the
selected semantic role from ``TypedAppearanceInput`` into the COLOR domain and
returns that canonical linear-sRGB RGBA value unchanged.  BASE and COLOR are
therefore distinct domains even though they may share the same upstream color
role: BASE is the legacy-compatible base-color field, while COLOR is the typed
color-domain hand-off.

No saturation, contrast, vibrance, temperature, pattern generation, palette
mixing, alpha compositing, lighting, shading, material response, gamut mapping or
renderer-specific post-processing is performed here.  Those operations require
separate contracts and are deliberately outside V1.31.
"""

from dataclasses import dataclass

from visual_engine.runtime.appearance_contract import AppearanceDomain, DomainContractError
from visual_engine.runtime.appearance_role_bridge import AppearanceRoleContribution
from visual_engine.runtime.domain_input_factory import build_domain_resolution_input
from visual_engine.runtime.domain_resolution import (
    DomainResolutionInput,
    DomainResolutionProvenance,
    DomainResolutionResult,
    DomainResolutionStatus,
    DomainResolvedField,
    validate_domain_resolution_result,
)
from visual_engine.runtime.identity import stable_digest


COLOR_RESOLVER_ID = "color.authoritative-role"
COLOR_RESOLVER_VERSION = "1"
COLOR_DOMAIN_INPUT_VERSION = "1"


class ColorResolutionError(DomainContractError):
    """Raised for malformed COLOR resolver inputs or semantic contradictions."""


@dataclass(frozen=True, slots=True)
class TypedColorInput:
    """Minimal COLOR-domain projection of the canonical typed appearance input.

    Only the selected role is retained.  In particular, contour, material,
    opacity, visibility, state and renderer/geometry data are intentionally absent
    from the COLOR identity so an unrelated change cannot invalidate this domain.
    """

    target_id: str
    role_contribution: AppearanceRoleContribution
    fingerprint: str

    def __post_init__(self) -> None:
        if not self.target_id:
            raise ColorResolutionError("typed COLOR target_id must not be empty")
        if not isinstance(self.role_contribution, AppearanceRoleContribution):
            raise ColorResolutionError("typed COLOR input requires AppearanceRoleContribution")
        if self.role_contribution.target_id != self.target_id:
            raise ColorResolutionError("typed COLOR role target does not match target_id")
        expected = stable_digest({
            "version": COLOR_DOMAIN_INPUT_VERSION,
            "target_id": self.target_id,
            "role_contribution": self.role_contribution.fingerprint,
        })
        if self.fingerprint != expected:
            raise ColorResolutionError("typed COLOR input fingerprint mismatch")

    @classmethod
    def from_typed_appearance_input(cls, typed_input) -> "TypedColorInput":
        """Project the canonical appearance envelope without inheriting unrelated fields."""
        from visual_engine.runtime.typed_appearance_input import TypedAppearanceInput

        if not isinstance(typed_input, TypedAppearanceInput):
            raise TypeError("typed_input must be TypedAppearanceInput")
        role = typed_input.role_contribution
        payload = {
            "version": COLOR_DOMAIN_INPUT_VERSION,
            "target_id": typed_input.target_id,
            "role_contribution": role.fingerprint,
        }
        return cls(
            target_id=typed_input.target_id,
            role_contribution=role,
            fingerprint=stable_digest(payload),
        )

    @classmethod
    def from_role_contribution(cls, role: AppearanceRoleContribution) -> "TypedColorInput":
        """Build the smallest COLOR input directly from one validated role."""
        if not isinstance(role, AppearanceRoleContribution):
            raise TypeError("role must be AppearanceRoleContribution")
        payload = {
            "version": COLOR_DOMAIN_INPUT_VERSION,
            "target_id": role.target_id,
            "role_contribution": role.fingerprint,
        }
        return cls(role.target_id, role, stable_digest(payload))

    def to_domain_input(self, *, dependencies=()) -> DomainResolutionInput:
        """Create the generic COLOR transaction envelope with typed role authority."""
        return build_color_resolution_input_from_typed(self, dependencies=dependencies)


def build_color_resolution_input_from_typed(
    typed_input: TypedColorInput | object,
    *,
    dependencies=(),
    resolver_id: str = COLOR_RESOLVER_ID,
    resolver_version: str = COLOR_RESOLVER_VERSION,
    contract_version: str = "1",
) -> DomainResolutionInput:
    """Build COLOR input from the minimal typed projection, never from hex text."""
    if not isinstance(typed_input, TypedColorInput):
        raise TypeError("typed_input must be TypedColorInput")
    return build_domain_resolution_input(
        typed_input.target_id,
        AppearanceDomain.COLOR,
        contributions=(),
        dependencies=dependencies,
        resolver_id=resolver_id,
        resolver_version=resolver_version,
        contract_version=contract_version,
        role_contribution=typed_input.role_contribution,
    )


def resolve_color_domain(input_data: DomainResolutionInput) -> DomainResolutionResult:
    """Resolve one selected typed color role as an unchanged canonical color.

    A COLOR contribution alongside the typed role is rejected by the generic
    input contract, preventing a second authority.  Missing typed role is also a
    rejection: V1.31 deliberately has no implicit legacy COLOR fallback.
    """
    if input_data.domain is not AppearanceDomain.COLOR:
        raise ColorResolutionError("COLOR resolver received an input for another appearance domain")

    role = input_data.role_contribution
    if role is None:
        return _rejected(
            input_data,
            "COLOR_NO_TYPED_ROLE",
            "V1.31 COLOR resolution requires a typed AppearanceRoleContribution",
        )

    # The canonical role object is already validated and carries the exact
    # canonical linear-sRGB value.  Returning it directly avoids a needless
    # linear -> sRGB -> linear round trip and therefore avoids quantization drift.
    fields = [
        DomainResolvedField("color", role.canonical_color),
        DomainResolvedField("role", role.role.value),
        DomainResolvedField("source", role.source.value),
    ]
    if role.authored_srgb is not None:
        fields.append(DomainResolvedField("authored_srgb", role.authored_srgb))
    fields.sort(key=lambda field: field.name)

    result = DomainResolutionResult(
        target_id=input_data.target_id,
        domain=AppearanceDomain.COLOR,
        status=DomainResolutionStatus.RESOLVED,
        input_digest=input_data.input_digest,
        resolver_id=input_data.resolver_id,
        resolver_version=input_data.resolver_version,
        resolved_fields=tuple(fields),
        provenance=DomainResolutionProvenance(
            target_id=input_data.target_id,
            domain=AppearanceDomain.COLOR,
            contribution_ids=("role:" + role.fingerprint,),
            dependency_names=tuple(sorted(item.name for item in input_data.dependencies)),
            resolver_id=input_data.resolver_id,
            resolver_version=input_data.resolver_version,
            role_bridge_fingerprint=role.fingerprint,
            role_authority_component_id=role.authority_component_id,
            role_source_id=role.source_id,
            role_lineage=role.lineage,
        ),
        dependency_digest=stable_digest(input_data.dependencies),
    )
    validate_domain_resolution_result(result, input_data)
    return result


def resolve_color_domain_from_typed(typed_input, *, dependencies=()) -> DomainResolutionResult:
    """Resolve COLOR from a canonical appearance envelope via the minimal projection."""
    color_input = TypedColorInput.from_typed_appearance_input(typed_input)
    return resolve_color_domain(color_input.to_domain_input(dependencies=dependencies))


def color_domain_fingerprint(typed_input) -> str:
    """Return COLOR identity that excludes material, geometry and renderer state."""
    return TypedColorInput.from_typed_appearance_input(typed_input).fingerprint


def color_domain_invalidation(graph, target_component_id: str, changed_component_id: str, request) -> tuple[bool, tuple[str, ...]]:
    """Delegate targeted authority invalidation to the existing role bridge.

    COLOR consumes the selected semantic role, so only authorities that can change
    that role are dependencies.  Geometry and unrelated siblings are not promoted
    into the COLOR invalidation set.
    """
    from visual_engine.runtime.appearance_role_bridge import role_bridge_invalidation

    affects, reasons = role_bridge_invalidation(
        graph, target_component_id, changed_component_id, request
    )
    if not affects:
        return False, ()
    return True, tuple(f"COLOR depends on selected role: {reason}" for reason in reasons)


def _rejected(input_data: DomainResolutionInput, code: str, message: str) -> DomainResolutionResult:
    result = DomainResolutionResult(
        target_id=input_data.target_id,
        domain=AppearanceDomain.COLOR,
        status=DomainResolutionStatus.REJECTED,
        input_digest=input_data.input_digest,
        resolver_id=input_data.resolver_id,
        resolver_version=input_data.resolver_version,
        unresolved_reasons=(f"{code}: {message}",),
        dependency_digest=stable_digest(input_data.dependencies),
    )
    validate_domain_resolution_result(result, input_data)
    return result
