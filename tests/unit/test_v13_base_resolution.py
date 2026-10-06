import pytest

from visual_engine.runtime.appearance_contract import (
    AppearanceContribution,
    AppearanceDomain,
    DomainContractError,
)
from visual_engine.runtime.base_resolution import (
    BASE_RESOLVER_ID,
    BASE_RESOLVER_VERSION,
    BaseResolutionError,
    build_base_resolution_input,
    resolve_base_domain,
)
from visual_engine.runtime.domain_resolution import (
    DomainDependency,
    DomainResolutionStatus,
)
from visual_engine.runtime.versioning import stable_digest


def _base(cid="b1", color="#AABBCC", opacity=1.0):
    return AppearanceContribution(
        cid,
        AppearanceDomain.BASE,
        "source",
        (("base_color", color),),
        opacity=opacity,
    )


def _input(contributions=(_base(),), **kwargs):
    return build_base_resolution_input(
        "eye",
        contributions=contributions,
        dependencies={"appearance_layers": stable_digest("layers")},
        **kwargs,
    )


def test_single_opaque_base_contribution_resolves_authoritative_color():
    result = resolve_base_domain(_input())
    assert result.status is DomainResolutionStatus.RESOLVED
    assert result.resolved_fields == (result.resolved_fields[0],)
    assert result.resolved_fields[0].name == "base_color"
    assert result.resolved_fields[0].value == "#aabbcc"
    assert result.provenance is not None
    assert result.provenance.contribution_ids == ("b1",)


def test_resolver_identity_is_explicit_and_stable_by_default():
    data = _input()
    assert data.resolver_id == BASE_RESOLVER_ID
    assert data.resolver_version == BASE_RESOLVER_VERSION
    assert resolve_base_domain(data).result_digest == resolve_base_domain(data).result_digest


def test_rgba_base_color_is_preserved_without_interpreting_alpha():
    result = resolve_base_domain(_input((_base(color="#AABBCC80"),)))
    assert result.status is DomainResolutionStatus.RESOLVED
    assert result.resolved_fields[0].value == "#aabbcc80"


def test_zero_contributions_reject_without_fabricating_a_default_color():
    result = resolve_base_domain(_input(()))
    assert result.status is DomainResolutionStatus.REJECTED
    assert result.resolved_fields == ()
    assert "BASE_NO_AUTHORITY" in result.unresolved_reasons[0]


def test_multiple_base_contributions_reject_without_implicit_precedence():
    result = resolve_base_domain(_input((_base("b1"), _base("b2", "#112233"))))
    assert result.status is DomainResolutionStatus.REJECTED
    assert "BASE_MULTIPLE_AUTHORITIES" in result.unresolved_reasons[0]


def test_translucent_base_contribution_rejects_without_an_underlay():
    result = resolve_base_domain(_input((_base(opacity=0.5),)))
    assert result.status is DomainResolutionStatus.REJECTED
    assert "BASE_TRANSLUCENT_AUTHORITY" in result.unresolved_reasons[0]


def test_input_state_changes_invalidate_base_resolution_identity_conservatively():
    a = _input(active_states=())
    b = _input(active_states=("wet",))
    assert a.input_digest != b.input_digest
    assert resolve_base_domain(a).result_digest != resolve_base_domain(b).result_digest


def test_dependency_changes_invalidate_base_result_identity():
    a = _input()
    b = build_base_resolution_input(
        "eye",
        contributions=(_base(),),
        dependencies={"appearance_layers": stable_digest("changed")},
    )
    assert a.input_digest != b.input_digest
    assert resolve_base_domain(a).result_digest != resolve_base_domain(b).result_digest


def test_dependency_provenance_is_complete():
    data = _input()
    result = resolve_base_domain(data)
    assert result.provenance.dependency_names == ("appearance_layers",)
    assert result.dependency_digest == stable_digest(data.dependencies)


def test_custom_resolver_identity_is_carried_without_rewriting():
    data = _input(resolver_id="test.base", resolver_version="7")
    result = resolve_base_domain(data)
    assert result.resolver_id == "test.base"
    assert result.resolver_version == "7"
    assert result.provenance.resolver_id == "test.base"
    assert result.provenance.resolver_version == "7"


def test_wrong_domain_is_rejected_at_input_boundary():
    with pytest.raises(DomainContractError):
        build_base_resolution_input(
            "eye",
            contributions=(AppearanceContribution(
                "c1", AppearanceDomain.COLOR, "source", (("saturation", 0.2),)
            ),),
        )


def test_wrong_domain_direct_resolver_call_fails_closed():
    from visual_engine.runtime.domain_resolution import build_domain_resolution_input

    data = build_domain_resolution_input(
        "eye",
        AppearanceDomain.COLOR,
        contributions=(AppearanceContribution(
            "c1", AppearanceDomain.COLOR, "source", (("saturation", 0.2),)
        ),),
        resolver_id=BASE_RESOLVER_ID,
        resolver_version=BASE_RESOLVER_VERSION,
    )
    with pytest.raises(BaseResolutionError):
        resolve_base_domain(data)


def test_malformed_base_payload_cannot_reach_algorithm():
    with pytest.raises(DomainContractError):
        build_base_resolution_input(
            "eye",
            contributions=(AppearanceContribution(
                "b1", AppearanceDomain.BASE, "source", (("base_color", "#fff"),)
            ),),
        )


def test_rejected_result_has_no_resolved_fields():
    result = resolve_base_domain(_input((_base(opacity=0.0),)))
    assert result.status is DomainResolutionStatus.REJECTED
    assert result.resolved_fields == ()
    assert result.provenance is None
