from __future__ import annotations

"""Deterministic resolver for the MATERIAL appearance domain.

The MATERIAL resolver is intentionally an authoritative-record resolver, not a
shader or a physical-material simulator.  The current domain contract exposes
five material fields (name, roughness, metallic, transmission and emission), but
does not define precedence between multiple material contributions.  Therefore
this resolver accepts exactly one non-empty opaque contribution and returns its
validated fields unchanged.

Keeping this boundary narrow prevents accidental semantics such as averaging
roughness, OR-ing metallic flags, summing emission, or blending transmission.
Those operations require an explicit composition model and are deliberately left
for a later checkpoint.
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


MATERIAL_RESOLVER_ID = "material.authoritative"
MATERIAL_RESOLVER_VERSION = "1"


class MaterialResolutionError(DomainContractError):
    """Raised for malformed MATERIAL resolver inputs."""


def resolve_material_domain(
    input_data: DomainResolutionInput,
) -> DomainResolutionResult:
    """Resolve one authoritative MATERIAL contribution.

    The resolver deliberately does not derive or combine material properties.
    Every field returned is copied from the single validated contribution.  This
    makes the operation deterministic and auditable while avoiding unsupported
    physical or artistic assumptions.

    Fail-closed rules:

    * a non-MATERIAL input is a programming error and raises immediately;
    * zero contributions reject because no material authority exists;
    * multiple contributions reject because no precedence/composition rule exists;
    * an empty contribution rejects because it contains no material information;
    * translucent contribution opacity rejects because there is no underlay
      semantics at the MATERIAL boundary;
    * valid fields are returned in canonical field-name order without changing
      their values.
    """
    if input_data.domain is not AppearanceDomain.MATERIAL:
        raise MaterialResolutionError(
            "MATERIAL resolver received an input for another appearance domain"
        )

    contributions = input_data.contributions
    if not contributions:
        return _rejected(
            input_data,
            "MATERIAL_NO_AUTHORITY",
            "no MATERIAL contribution is available",
        )

    if len(contributions) != 1:
        return _rejected(
            input_data,
            "MATERIAL_MULTIPLE_AUTHORITIES",
            "multiple MATERIAL contributions have no declared precedence or composition rule",
        )

    contribution = contributions[0]
    values = dict(contribution.values)
    if not values:
        return _rejected(
            input_data,
            "MATERIAL_EMPTY_AUTHORITY",
            "the MATERIAL contribution contains no material fields",
        )

    if contribution.opacity != 1.0:
        return _rejected(
            input_data,
            "MATERIAL_TRANSLUCENT_AUTHORITY",
            "a translucent MATERIAL contribution cannot be resolved without explicit composition semantics",
        )

    # Values were already validated by DomainResolutionInput against the closed
    # MATERIAL contract.  We only preserve them here; this resolver does not
    # normalize physical parameters or invent defaults for absent fields.
    fields = tuple(
        DomainResolvedField(name, values[name])
        for name in sorted(values)
    )
    result = DomainResolutionResult(
        target_id=input_data.target_id,
        domain=AppearanceDomain.MATERIAL,
        status=DomainResolutionStatus.RESOLVED,
        input_digest=input_data.input_digest,
        resolver_id=input_data.resolver_id,
        resolver_version=input_data.resolver_version,
        resolved_fields=fields,
        provenance=DomainResolutionProvenance(
            target_id=input_data.target_id,
            domain=AppearanceDomain.MATERIAL,
            contribution_ids=(contribution.contribution_id,),
            dependency_names=tuple(sorted(item.name for item in input_data.dependencies)),
            resolver_id=input_data.resolver_id,
            resolver_version=input_data.resolver_version,
        ),
        dependency_digest=stable_digest(input_data.dependencies),
    )
    validate_domain_resolution_result(result, input_data)
    return result


def build_material_resolution_input(
    target_id: str,
    *,
    contributions=(),
    active_states=(),
    dependencies=(),
    resolver_id: str = MATERIAL_RESOLVER_ID,
    resolver_version: str = MATERIAL_RESOLVER_VERSION,
    contract_version: str = "1",
) -> DomainResolutionInput:
    """Build a MATERIAL input through the generic resolver-input factory."""
    from visual_engine.runtime.domain_input_factory import build_domain_resolution_input

    return build_domain_resolution_input(
        target_id,
        AppearanceDomain.MATERIAL,
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
    """Create and validate one deterministic rejected MATERIAL result."""
    result = DomainResolutionResult(
        target_id=input_data.target_id,
        domain=AppearanceDomain.MATERIAL,
        status=DomainResolutionStatus.REJECTED,
        input_digest=input_data.input_digest,
        resolver_id=input_data.resolver_id,
        resolver_version=input_data.resolver_version,
        unresolved_reasons=(f"{code}: {message}",),
        dependency_digest=stable_digest(input_data.dependencies),
    )
    validate_domain_resolution_result(result, input_data)
    return result
