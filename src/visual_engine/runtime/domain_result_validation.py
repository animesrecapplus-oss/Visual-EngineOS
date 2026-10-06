from __future__ import annotations  # V1.51: keep runtime imports acyclic while typing domain envelopes.

from visual_engine.runtime.appearance_contract import DomainContractError, _validate_field  # V1.51: reuse the canonical field contract validator.
from visual_engine.runtime.versioning import stable_digest  # V1.51: validate the dependency digest against canonical input dependencies.


def _contract_for(domain):  # V1.51: resolve the canonical semantic contract without duplicating the domain registry.
    from visual_engine.runtime.appearance_contract import DOMAIN_CONTRACTS  # V1.51: lazy import prevents a new module cycle.
    contract = DOMAIN_CONTRACTS.get(domain)  # V1.51: lookup the one authoritative domain contract.
    if contract is None:  # V1.51: fail closed when a domain has no registered contract.
        raise DomainContractError(f"no semantic contract is registered for '{domain.value}'")  # V1.51: make the missing contract explicit.
    return contract  # V1.51: return the canonical contract used for output validation.


def validate_domain_resolution_result(  # V1.51: canonical owner for result/input semantic validation.
    result: "DomainResolutionResult",  # V1.51: the immutable resolver result being checked.
    input_data: "DomainResolutionInput",  # V1.51: the immutable input envelope that produced the result.
) -> None:  # V1.51: validation is fail-closed and returns no transformed value.
    if result.target_id != input_data.target_id:  # V1.51: prevent cross-target result reuse.
        raise DomainContractError("domain result target does not match its input")  # V1.51: reject mismatched ownership.
    if result.domain is not input_data.domain:  # V1.51: prevent cross-domain result reuse.
        raise DomainContractError("domain result domain does not match its input")  # V1.51: reject semantic-domain mismatch.
    if result.input_digest != input_data.input_digest:  # V1.51: prevent stale or substituted input envelopes.
        raise DomainContractError("domain result was produced from a different input digest")  # V1.51: reject stale provenance.
    if result.resolver_id != input_data.resolver_id or result.resolver_version != input_data.resolver_version:  # V1.51: bind output to resolver identity.
        raise DomainContractError("domain result resolver identity does not match its input")  # V1.51: reject resolver drift.
    contract = _contract_for(result.domain)  # V1.51: obtain the canonical output vocabulary.
    field_map = contract.field_map  # V1.51: index declared fields once for deterministic validation.
    for field in result.resolved_fields:  # V1.51: inspect every produced field against the domain contract.
        field_contract = field_map.get(field.name)  # V1.51: resolve the declared field by semantic name.
        if field_contract is None:  # V1.51: unknown output fields are forbidden.
            raise DomainContractError(f"domain '{result.domain.value}' does not declare output field '{field.name}'")  # V1.51: fail closed on vocabulary expansion.
        _validate_field(field_contract, field.value)  # V1.51: enforce the existing field type/range contract.
    if result.status.value == "resolved":  # V1.51: resolved status requires complete required output without importing the owner module.
        required = {field.name for field in contract.fields if field.required}  # V1.51: derive requirements from the canonical contract.
        produced = {field.name for field in result.resolved_fields}  # V1.51: record the actual output vocabulary.
        missing = sorted(required - produced)  # V1.51: compute missing required fields deterministically.
        if missing:  # V1.51: reject an apparently resolved result with incomplete output.
            raise DomainContractError(f"resolved domain '{result.domain.value}' is missing required output fields: {', '.join(missing)}")  # V1.51: expose the exact missing fields.
    if result.provenance is not None:  # V1.51: provenance is optional only for unresolved/rejected states.
        expected_role = input_data.role_contribution  # V1.51: capture the typed role source used by the input.
        if expected_role is not None:  # V1.51: role provenance must match the typed input exactly.
            if result.provenance.role_bridge_fingerprint != expected_role.fingerprint:  # V1.51: protect role bridge lineage identity.
                raise DomainContractError("domain result role bridge fingerprint does not match input")  # V1.51: reject stale role provenance.
            if result.provenance.role_authority_component_id != expected_role.authority_component_id:  # V1.51: protect authority ownership.
                raise DomainContractError("domain result role authority does not match input")  # V1.51: reject authority drift.
            if result.provenance.role_source_id != expected_role.source_id:  # V1.51: protect role source identity.
                raise DomainContractError("domain result role source does not match input")  # V1.51: reject source drift.
            if result.provenance.role_lineage != expected_role.lineage:  # V1.51: protect the complete role lineage.
                raise DomainContractError("domain result role lineage does not match input")  # V1.51: reject lineage mutation.
        elif result.provenance.role_bridge_fingerprint is not None:  # V1.51: forbid unbacked role provenance claims.
            raise DomainContractError("domain result cannot claim role bridge provenance without typed role input")  # V1.51: fail closed on fabricated lineage.
        expected_ids = ("role:" + input_data.role_contribution.fingerprint,) if input_data.role_contribution is not None else tuple(sorted(item.contribution_id for item in input_data.contributions))  # V1.51: derive expected contribution provenance deterministically.
        if result.provenance.contribution_ids != expected_ids:  # V1.51: protect contribution lineage identity.
            raise DomainContractError("domain result provenance contribution set does not match input")  # V1.51: reject contribution substitution.
        expected_dependencies = tuple(sorted(item.name for item in input_data.dependencies))  # V1.51: derive expected dependency names canonically.
        if result.provenance.dependency_names != expected_dependencies:  # V1.51: protect dependency lineage identity.
            raise DomainContractError("domain result provenance dependency set does not match input")  # V1.51: reject dependency substitution.
    expected_dependency_digest = stable_digest(input_data.dependencies)  # V1.51: recompute the dependency identity from canonical input.
    if result.dependency_digest != expected_dependency_digest:  # V1.51: prevent stale dependency evidence from being accepted.
        raise DomainContractError("domain result dependency digest does not match input dependencies")  # V1.51: reject dependency digest drift.
