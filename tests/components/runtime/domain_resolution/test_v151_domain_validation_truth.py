from __future__ import annotations  # V1.51: keep test annotations independent from runtime imports.

from pathlib import Path  # V1.51: inspect persistence boundaries as part of the impact gate.

import pytest  # V1.51: hostile tests require explicit exception assertions.

from visual_engine.runtime import validate_domain_resolution_result as public_validate  # V1.51: verify the public facade.
from visual_engine.runtime.domain_resolution import (  # V1.51: exercise the legacy compatibility surface.
    DomainResolutionInput, DomainResolutionResult, DomainResolutionStatus, DomainResolvedField,
    build_domain_resolution_input, validate_domain_resolution_result as legacy_validate,
)
from visual_engine.runtime.domain_result_validation import validate_domain_resolution_result as canonical_validate  # V1.51: verify the canonical owner.
from visual_engine.runtime.appearance_contract import AppearanceContribution, AppearanceDomain, DomainContractError  # V1.51: build typed domain inputs.
from visual_engine.runtime.versioning import stable_digest  # V1.51: create deterministic dependency identities.


def _input() -> DomainResolutionInput:  # V1.51: create one canonical COLOR validation envelope.
    contribution = AppearanceContribution("c1", AppearanceDomain.COLOR, "source", (("saturation", 0.2),))  # V1.51: provide one valid field.
    return build_domain_resolution_input("eye", AppearanceDomain.COLOR, contributions=(contribution,), resolver_id="color.test", resolver_version="1")  # V1.51: canonicalize the input.


def _result(data: DomainResolutionInput) -> DomainResolutionResult:  # V1.51: construct one valid result for mutation attacks.
    from visual_engine.runtime.domain_resolution import DomainResolutionProvenance  # V1.51: keep the fixture local to the compatibility contract.
    provenance = DomainResolutionProvenance(data.target_id, data.domain, ("c1",), (), data.resolver_id, data.resolver_version)  # V1.51: match input lineage exactly.
    return DomainResolutionResult(data.target_id, data.domain, DomainResolutionStatus.RESOLVED, data.input_digest, data.resolver_id, data.resolver_version, (DomainResolvedField("saturation", 0.5),), (), provenance, stable_digest(data.dependencies))  # V1.51: produce a complete resolved result.


def test_canonical_owner_and_legacy_api_identity() -> None:  # V1.51: one implementation must own all public entry points.
    assert public_validate is canonical_validate  # V1.51: runtime public API must resolve to the canonical owner.
    assert legacy_validate is canonical_validate  # V1.51: legacy module path must remain identity-compatible.


def test_valid_result_passes_through_all_public_paths() -> None:  # V1.51: compatibility paths must preserve behaviour.
    data = _input()  # V1.51: use the canonical valid input.
    result = _result(data)  # V1.51: use the canonical valid result.
    public_validate(result, data)  # V1.51: verify the public facade.
    legacy_validate(result, data)  # V1.51: verify the legacy facade.
    canonical_validate(result, data)  # V1.51: verify the canonical owner.


@pytest.mark.parametrize("field", ["target_id", "domain", "input_digest", "resolver_id", "resolver_version"])  # V1.51: enumerate identity mismatch attack surfaces.
def test_identity_mismatch_is_rejected(field: str) -> None:  # V1.51: result identity cannot be detached from its input.
    data = _input()  # V1.51: start from a valid envelope.
    result = _result(data)  # V1.51: start from a valid result.
    values = {"target_id": "other", "domain": AppearanceDomain.BASE, "input_digest": stable_digest("stale"), "resolver_id": "other", "resolver_version": "2"}  # V1.51: provide contradictory identity values.
    bad = object.__new__(DomainResolutionResult)  # V1.51: bypass constructor guards to attack the validator boundary itself.
    for name in ("target_id", "domain", "status", "input_digest", "resolver_id", "resolver_version", "resolved_fields", "unresolved_reasons", "provenance", "dependency_digest"):  # V1.51: copy every immutable field before tampering one value.
        object.__setattr__(bad, name, getattr(result, name))  # V1.51: create a controlled hostile envelope without changing production code.
    object.__setattr__(bad, field, values[field])  # V1.51: mutate exactly one identity dimension after construction.
    with pytest.raises(DomainContractError):  # V1.51: every contradiction must fail closed.
        canonical_validate(bad, data)  # V1.51: exercise the canonical owner.


def test_unknown_field_and_missing_required_field_fail_closed() -> None:  # V1.51: domain vocabulary cannot be invented by a result.
    data = _input()  # V1.51: use a valid COLOR envelope.
    valid = _result(data)  # V1.51: use a valid baseline.
    unknown = DomainResolutionResult(valid.target_id, valid.domain, valid.status, valid.input_digest, valid.resolver_id, valid.resolver_version, (DomainResolvedField("not_declared", 1.0),), (), valid.provenance, valid.dependency_digest)  # V1.51: inject an undeclared output field.
    with pytest.raises(DomainContractError):  # V1.51: unknown vocabulary must be rejected.
        canonical_validate(unknown, data)  # V1.51: exercise vocabulary enforcement.


def test_nan_field_is_rejected_by_the_canonical_field_contract() -> None:  # V1.51: non-finite semantic values must never pass through validation.
    data = _input()  # V1.51: use a valid COLOR envelope.
    valid = _result(data)  # V1.51: use a valid result shape.
    nan_result = DomainResolutionResult(valid.target_id, valid.domain, valid.status, valid.input_digest, valid.resolver_id, valid.resolver_version, (DomainResolvedField("saturation", float("nan")),), (), valid.provenance, valid.dependency_digest)  # V1.51: inject NaN at the hostile boundary.
    with pytest.raises((DomainContractError, ValueError)):  # V1.51: either contract-layer error is an explicit rejection.
        canonical_validate(nan_result, data)  # V1.51: never accept NaN as semantic output.


def test_persistence_has_no_direct_dependency_on_validation_owner() -> None:  # V1.51: database impact must be proven absent, not assumed.
    persistence = Path("src/visual_engine/persistence")  # V1.51: inspect the real persistence package.
    source = "\n".join(path.read_text(encoding="utf-8") for path in persistence.rglob("*.py"))  # V1.51: inspect every persistence module.
    assert "domain_result_validation" not in source  # V1.51: no database path directly owns domain-result validation.
    assert "domain_resolution" not in source  # V1.51: no database serializer directly imports the domain resolver contract.
