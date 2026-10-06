from __future__ import annotations

from visual_engine.runtime import DomainResolutionResult as PublicResult
from visual_engine.runtime.domain_resolution import (
    DomainResolutionProvenance,
    DomainResolutionResult,
    DomainResolutionStatus,
    DomainResolvedField,
    build_domain_resolution_input,
)
from visual_engine.runtime.domain_result_contract import (
    DomainResolutionProvenance as CanonicalProvenance,
    DomainResolutionResult as CanonicalResult,
    DomainResolutionStatus as CanonicalStatus,
    DomainResolvedField as CanonicalField,
)
from visual_engine.runtime.appearance_contract import AppearanceContribution, AppearanceDomain
from visual_engine.runtime.versioning import stable_digest


def _input():
    contribution = AppearanceContribution("c1", AppearanceDomain.COLOR, "source", (("saturation", 0.2),))
    return build_domain_resolution_input("eye", AppearanceDomain.COLOR, contributions=(contribution,), resolver_id="color.test", resolver_version="1")


def _result(data):
    provenance = DomainResolutionProvenance(data.target_id, data.domain, ("c1",), (), data.resolver_id, data.resolver_version)
    return DomainResolutionResult(
        data.target_id, data.domain, DomainResolutionStatus.RESOLVED, data.input_digest,
        data.resolver_id, data.resolver_version, (DomainResolvedField("saturation", 0.5),),
        (), provenance, stable_digest(data.dependencies),
    )


def test_moved_types_have_one_canonical_owner_and_legacy_identity():
    assert DomainResolutionResult is CanonicalResult is PublicResult
    assert DomainResolutionProvenance is CanonicalProvenance
    assert DomainResolutionStatus is CanonicalStatus
    assert DomainResolvedField is CanonicalField


def test_result_digest_and_provenance_digest_remain_deterministic():
    data = _input()
    first = _result(data)
    second = _result(data)
    assert first.result_digest == second.result_digest
    assert first.provenance is not None
    assert first.provenance.digest == second.provenance.digest


def test_result_contract_rejects_hostile_constructor_states():
    data = _input()
    valid = _result(data)
    for status, reasons in ((DomainResolutionStatus.RESOLVED, ("unexpected",)), (DomainResolutionStatus.REJECTED, ())):
        try:
            DomainResolutionResult(
                valid.target_id, valid.domain, status, valid.input_digest,
                valid.resolver_id, valid.resolver_version, (), reasons, None,
                valid.dependency_digest,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("invalid result state was accepted")


def test_result_contract_rejects_bad_digest_and_field_order():
    data = _input()
    provenance = DomainResolutionProvenance(data.target_id, data.domain, ("c1",), (), data.resolver_id, data.resolver_version)
    try:
        DomainResolutionResult("eye", data.domain, DomainResolutionStatus.RESOLVED, "nan", data.resolver_id, "1", (), (), provenance, stable_digest(data.dependencies))
    except ValueError:
        pass
    else:
        raise AssertionError("invalid SHA-256 digest was accepted")
    try:
        DomainResolutionResult("eye", data.domain, DomainResolutionStatus.RESOLVED, data.input_digest, data.resolver_id, "1", (CanonicalField("z", 1), CanonicalField("a", 2)), (), provenance, stable_digest(data.dependencies))
    except ValueError:
        pass
    else:
        raise AssertionError("non-canonical field ordering was accepted")


def test_result_contract_rejects_impossible_runtime_types():
    data = _input()
    digest = stable_digest(data.dependencies)
    for status in ("bogus", 1, None):
        try:
            DomainResolutionResult("eye", data.domain, status, data.input_digest, "r", "1", (), ("reason",), None, digest)
        except TypeError:
            pass
        else:
            raise AssertionError("invalid status type was accepted")
    for domain in ("color", None, 1):
        try:
            DomainResolutionResult("eye", domain, DomainResolutionStatus.UNRESOLVED, data.input_digest, "r", "1", (), ("reason",), None, digest)
        except TypeError:
            pass
        else:
            raise AssertionError("invalid domain type was accepted")


def test_result_contract_rejects_incoherent_container_and_provenance_types():
    data = _input()
    digest = stable_digest(data.dependencies)
    base = ("eye", data.domain, DomainResolutionStatus.RESOLVED, data.input_digest, "r", "1")
    cases = [
        (*base, [CanonicalField("saturation", 0.5)], (), None, digest),
        (*base, (), ["reason"], None, digest),
        (*base, (), (), object(), digest),
    ]
    for values in cases:
        try:
            DomainResolutionResult(*values)
        except TypeError:
            pass
        else:
            raise AssertionError("incoherent result container type was accepted")
