import pytest

from visual_engine.runtime.version_policy import RESOLUTION_VERSION
from visual_engine.runtime.appearance_contract import AppearanceContribution, AppearanceDomain, DomainContractError
from visual_engine.runtime.domain_resolution import (
    DomainDependency,
    DomainResolutionInput,
    DomainResolutionProvenance,
    DomainResolutionResult,
    DomainResolutionStatus,
    DomainResolvedField,
    build_domain_resolution_input,
    unresolved_domain_result,
    validate_domain_resolution_result,
)
from visual_engine.runtime.versioning import stable_digest, VersionStamp


def _contribution(domain=AppearanceDomain.COLOR, cid="c1"):
    return AppearanceContribution(cid, domain, "source", (("saturation", 0.2),))


def _input(**kwargs):
    return build_domain_resolution_input(
        "eye", AppearanceDomain.COLOR,
        contributions=(_contribution(),),
        dependencies={"appearance_layers": stable_digest("layers")},
        resolver_id="color.contract",
        resolver_version="0",
        **kwargs,
    )


def _provenance(data):
    return DomainResolutionProvenance(
        target_id=data.target_id,
        domain=data.domain,
        contribution_ids=tuple(sorted(c.contribution_id for c in data.contributions)),
        dependency_names=tuple(sorted(d.name for d in data.dependencies)),
        resolver_id=data.resolver_id,
        resolver_version=data.resolver_version,
    )


def test_input_is_single_domain_and_canonical():
    data = _input(active_states=("wet", "open", "wet"))
    assert data.active_states == ("open", "wet")
    assert data.domain is AppearanceDomain.COLOR
    assert data.dependencies[0].name == "appearance_layers"
    assert len(data.input_digest) == 64


def test_mixed_domain_input_fails_closed():
    with pytest.raises(DomainContractError):
        build_domain_resolution_input(
            "eye", AppearanceDomain.COLOR,
            contributions=(_contribution(), _contribution(AppearanceDomain.MATERIAL, "m1")),
        )


def test_state_and_effect_cannot_enter_rendering_domain_resolver():
    with pytest.raises(DomainContractError):
        build_domain_resolution_input("eye", AppearanceDomain.STATE)
    with pytest.raises(DomainContractError):
        build_domain_resolution_input("eye", AppearanceDomain.EFFECT)


def test_dependencies_are_canonical_and_unique():
    digest = stable_digest("x")
    data = build_domain_resolution_input(
        "eye", AppearanceDomain.COLOR,
        dependencies=(DomainDependency("z", digest), DomainDependency("a", digest)),
    )
    assert tuple(d.name for d in data.dependencies) == ("a", "z")


def test_duplicate_dependency_names_fail():
    digest = stable_digest("x")
    with pytest.raises(ValueError):
        DomainResolutionInput(
            "eye", AppearanceDomain.COLOR,
            dependencies=(DomainDependency("a", digest), DomainDependency("a", digest)),
        )


def test_resolved_output_must_use_declared_domain_vocabulary_and_types():
    data = _input()
    result = DomainResolutionResult(
        target_id="eye", domain=AppearanceDomain.COLOR,
        status=DomainResolutionStatus.RESOLVED,
        input_digest=data.input_digest,
        resolver_id=data.resolver_id, resolver_version=data.resolver_version,
        resolved_fields=(DomainResolvedField("saturation", 0.5),),
        provenance=_provenance(data),
        dependency_digest=stable_digest(data.dependencies),
    )
    validate_domain_resolution_result(result, data)

    bad = DomainResolutionResult(
        target_id="eye", domain=AppearanceDomain.COLOR,
        status=DomainResolutionStatus.RESOLVED,
        input_digest=data.input_digest,
        resolver_id=data.resolver_id, resolver_version=data.resolver_version,
        resolved_fields=(DomainResolvedField("roughness", 0.5),),
        provenance=_provenance(data),
        dependency_digest=stable_digest(data.dependencies),
    )
    with pytest.raises(DomainContractError):
        validate_domain_resolution_result(bad, data)


def test_result_rejects_stale_input_digest():
    data = _input()
    result = DomainResolutionResult(
        target_id="eye", domain=data.domain,
        status=DomainResolutionStatus.RESOLVED,
        input_digest=stable_digest("stale"),
        resolver_id=data.resolver_id, resolver_version=data.resolver_version,
        resolved_fields=(DomainResolvedField("saturation", 0.5),),
        provenance=_provenance(data),
        dependency_digest=stable_digest(data.dependencies),
    )
    with pytest.raises(DomainContractError):
        validate_domain_resolution_result(result, data)


def test_partial_requires_explicit_reason():
    data = _input()
    with pytest.raises(ValueError):
        DomainResolutionResult(
            target_id="eye", domain=data.domain,
            status=DomainResolutionStatus.PARTIAL,
            input_digest=data.input_digest,
            resolver_id=data.resolver_id, resolver_version=data.resolver_version,
            resolved_fields=(DomainResolvedField("saturation", 0.5),),
            provenance=_provenance(data),
            dependency_digest=stable_digest(data.dependencies),
        )


def test_unresolved_result_does_not_claim_algorithmic_resolution():
    data = _input()
    result = unresolved_domain_result(data, "no domain algorithm registered")
    assert result.status is DomainResolutionStatus.UNRESOLVED
    assert result.resolved_fields == ()
    assert result.provenance is None
    validate_domain_resolution_result(result, data)


def test_resolved_result_requires_provenance():
    data = _input()
    with pytest.raises(ValueError):
        DomainResolutionResult(
            target_id="eye", domain=data.domain,
            status=DomainResolutionStatus.RESOLVED,
            input_digest=data.input_digest,
            resolver_id=data.resolver_id, resolver_version=data.resolver_version,
            resolved_fields=(DomainResolvedField("saturation", 0.5),),
            dependency_digest=stable_digest(data.dependencies),
        )


def test_resolved_base_output_must_satisfy_required_fields():
    data = build_domain_resolution_input(
        "eye", AppearanceDomain.BASE,
        contributions=(AppearanceContribution("b1", AppearanceDomain.BASE, "base", (("base_color", "#ffffff"),)),),
        resolver_id="base.contract", resolver_version="0",
    )
    provenance = DomainResolutionProvenance(
        "eye", data.domain, ("b1",), (), data.resolver_id, data.resolver_version
    )
    result = DomainResolutionResult(
        "eye", data.domain, DomainResolutionStatus.RESOLVED, data.input_digest,
        data.resolver_id, data.resolver_version, (), (), provenance,
        stable_digest(data.dependencies),
    )
    with pytest.raises(DomainContractError):
        validate_domain_resolution_result(result, data)


def test_rejected_result_requires_explicit_reason():
    data = _input()
    with pytest.raises(ValueError):
        DomainResolutionResult(
            "eye", data.domain, DomainResolutionStatus.REJECTED, data.input_digest,
            data.resolver_id, data.resolver_version, (), (), None,
            stable_digest(data.dependencies),
        )


def test_dependency_change_changes_input_identity():
    a = _input()
    b = build_domain_resolution_input(
        "eye", AppearanceDomain.COLOR,
        contributions=(_contribution(),),
        dependencies={"appearance_layers": stable_digest("different")},
        resolver_id="color.contract", resolver_version="0",
    )
    assert a.input_digest != b.input_digest


def test_result_digest_is_deterministic_and_versioning_changes_identity():
    data = _input()
    provenance = _provenance(data)
    a = DomainResolutionResult(
        "eye", data.domain, DomainResolutionStatus.RESOLVED, data.input_digest,
        data.resolver_id, data.resolver_version,
        (DomainResolvedField("saturation", 0.5),), (), provenance,
        stable_digest(data.dependencies),
    )
    b = DomainResolutionResult(
        "eye", data.domain, DomainResolutionStatus.RESOLVED, data.input_digest,
        data.resolver_id, data.resolver_version,
        (DomainResolvedField("saturation", 0.5),), (), provenance,
        stable_digest(data.dependencies),
    )
    assert a.result_digest == b.result_digest
    assert VersionStamp().resolution == RESOLUTION_VERSION
