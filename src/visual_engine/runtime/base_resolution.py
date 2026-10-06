from __future__ import annotations

"""Deterministic resolver for the BASE appearance domain.

BASE has a deliberately narrow semantic meaning at this stage: it identifies
one authoritative base color for one target. It is *not* a layer compositor,
material shader, alpha compositor, lighting solver, or color-grading engine.

The narrowness is intentional. ``AppearanceContribution.opacity`` is a
composition control, but a BASE resolver has no implicit background against
which a translucent contribution could be composited. Likewise, multiple BASE
contributions have no declared precedence in the current contract. Both cases
therefore fail closed instead of receiving an arbitrary ordering or blend rule.
"""

from visual_engine.runtime.appearance_contract import (
    AppearanceDomain,
    DomainContractError,
)
from visual_engine.runtime.domain_resolution import (
    DomainResolutionInput,
    DomainResolutionProvenance,
    DomainResolutionResult,
    DomainResolutionStatus,
    DomainResolvedField,
    validate_domain_resolution_result,
)
from visual_engine.runtime.versioning import stable_digest
from visual_engine.runtime.color_spaces import canonicalize_hex_color


BASE_RESOLVER_ID = "base.authoritative"
BASE_RESOLVER_VERSION = "2"


class BaseResolutionError(DomainContractError):
    """Raised only for malformed BASE resolver inputs or contract violations."""


def resolve_base_domain(
    input_data: DomainResolutionInput,
) -> DomainResolutionResult:
    """Resolve one authoritative BASE color without inventing composition rules.

    Rules are intentionally explicit:

    1. The input must target ``AppearanceDomain.BASE``.
    2. A V1.29 typed role contribution is the authoritative path.
    3. The legacy ``AppearanceContribution(base_color=...)`` path remains only
       as a compatibility adapter for pre-V1.29 callers.
    4. Typed role input must not coexist with a legacy BASE contribution.
    5. Alpha encoded inside ``#RRGGBBAA`` is preserved as data; no compositing
       or implicit underlay is introduced here.
    6. The returned field is a compatibility-domain value derived from the typed
       canonical color/representation; no mixing, gamut mapping or shading occurs.
    7. The result is validated again through the generic resolver contract.

    The canonical path therefore cannot silently select a second color authority.
    """
    if input_data.domain is not AppearanceDomain.BASE:
        raise BaseResolutionError(
            "BASE resolver received an input for another appearance domain"
        )

    role = input_data.role_contribution
    if role is not None:
        # V1.29 canonical path: the typed role owns the semantic color.  The
        # hexadecimal value is read only as its compatibility representation.
        base_color = role.legacy_base_color
        contribution_id = "role:" + role.fingerprint
        contribution_ids = (contribution_id,)
        role_kwargs = {
            "role_bridge_fingerprint": role.fingerprint,
            "role_authority_component_id": role.authority_component_id,
            "role_source_id": role.source_id,
            "role_lineage": role.lineage,
        }
    else:
        contributions = input_data.contributions
        if not contributions:
            return _rejected(input_data, "BASE_NO_AUTHORITY", "no BASE contribution is available")

        if len(contributions) != 1:
            return _rejected(
                input_data,
                "BASE_MULTIPLE_AUTHORITIES",
                "multiple BASE contributions have no declared precedence or composition rule",
            )

        contribution = contributions[0]
        values = dict(contribution.values)
        base_color = values.get("base_color")
        if base_color is None:
            return _rejected(
                input_data,
                "BASE_MISSING_COLOR",
                "the BASE contribution does not contain the required base_color field",
            )

        if contribution.opacity != 1.0:
            return _rejected(
                input_data,
                "BASE_TRANSLUCENT_AUTHORITY",
                "a translucent BASE contribution cannot be resolved without an explicit underlay",
            )
        contribution_ids = (contribution.contribution_id,)
        role_kwargs = {}

    result = DomainResolutionResult(
        target_id=input_data.target_id,
        domain=AppearanceDomain.BASE,
        status=DomainResolutionStatus.RESOLVED,
        input_digest=input_data.input_digest,
        resolver_id=input_data.resolver_id,
        resolver_version=input_data.resolver_version,
        resolved_fields=(DomainResolvedField("base_color", canonicalize_hex_color(base_color)),),
        provenance=DomainResolutionProvenance(
            target_id=input_data.target_id,
            domain=AppearanceDomain.BASE,
            contribution_ids=contribution_ids,
            dependency_names=tuple(sorted(item.name for item in input_data.dependencies)),
            resolver_id=input_data.resolver_id,
            resolver_version=input_data.resolver_version,
            **role_kwargs,
        ),
        dependency_digest=stable_digest(input_data.dependencies),
    )
    validate_domain_resolution_result(result, input_data)
    return result


def resolve_base_domain_from_typed(typed_input, *, dependencies=()):
    """Resolve BASE directly from the canonical typed appearance envelope."""
    return resolve_base_domain(typed_input.to_base_domain_input(dependencies=dependencies))


def build_base_resolution_input_from_typed(
    typed_input,
    *,
    dependencies=(),
    resolver_id: str = BASE_RESOLVER_ID,
    resolver_version: str = BASE_RESOLVER_VERSION,
    contract_version: str = "2",
) -> DomainResolutionInput:
    """Build BASE input directly from the V1.29/V1.30 typed envelope.

    The role contribution is forwarded unchanged.  No legacy hexadecimal value
    is reconstructed here, so a domain consumer cannot accidentally create a
    second color authority during migration.
    """
    from visual_engine.runtime.typed_appearance_input import TypedAppearanceInput

    if not isinstance(typed_input, TypedAppearanceInput):
        raise TypeError("typed_input must be TypedAppearanceInput")
    return build_base_resolution_input_from_role(
        typed_input.target_id,
        typed_input.role_contribution,
        dependencies=dependencies,
        resolver_id=resolver_id,
        resolver_version=resolver_version,
        contract_version=contract_version,
    )


def build_base_resolution_input_from_role(
    target_id: str,
    role_contribution,
    *,
    active_states=(),
    dependencies=(),
    resolver_id: str = BASE_RESOLVER_ID,
    resolver_version: str = BASE_RESOLVER_VERSION,
    contract_version: str = "2",
) -> DomainResolutionInput:
    """Build the canonical V1.29 BASE domain input from a typed role."""
    from visual_engine.runtime.domain_input_factory import build_domain_resolution_input

    return build_domain_resolution_input(
        target_id,
        AppearanceDomain.BASE,
        contributions=(),
        active_states=tuple(active_states),
        dependencies=dependencies,
        resolver_id=resolver_id,
        resolver_version=resolver_version,
        contract_version=contract_version,
        role_contribution=role_contribution,
    )


def build_base_resolution_input(
    target_id: str,
    *,
    contributions=(),
    active_states=(),
    dependencies=(),
    resolver_id: str = BASE_RESOLVER_ID,
    resolver_version: str = BASE_RESOLVER_VERSION,
    contract_version: str = "2",
) -> DomainResolutionInput:
    """Build a BASE-owned input with the canonical resolver identity.

    The function delegates canonicalization and validation to the generic
    ``build_domain_resolution_input`` factory rather than maintaining a second
    input model here.
    """
    from visual_engine.runtime.domain_input_factory import build_domain_resolution_input

    return build_domain_resolution_input(
        target_id,
        AppearanceDomain.BASE,
        contributions=tuple(contributions),
        active_states=tuple(active_states),
        dependencies=dependencies,
        resolver_id=resolver_id,
        resolver_version=resolver_version,
        contract_version=contract_version,
    )


def _rejected(
    input_data: DomainResolutionInput,
    code: str,
    message: str,
) -> DomainResolutionResult:
    """Create and validate a deterministic rejected BASE result."""
    result = DomainResolutionResult(
        target_id=input_data.target_id,
        domain=AppearanceDomain.BASE,
        status=DomainResolutionStatus.REJECTED,
        input_digest=input_data.input_digest,
        resolver_id=input_data.resolver_id,
        resolver_version=input_data.resolver_version,
        unresolved_reasons=(f"{code}: {message}",),
        dependency_digest=stable_digest(input_data.dependencies),
    )
    validate_domain_resolution_result(result, input_data)
    return result
