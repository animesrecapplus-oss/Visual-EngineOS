import pytest

from visual_engine.runtime.appearance_contract import (
    AppearanceContribution,
    AppearanceDomain,
    DomainContractError,
)
from visual_engine.runtime.material_resolution import (
    MATERIAL_RESOLVER_ID,
    MATERIAL_RESOLVER_VERSION,
    MaterialResolutionError,
    build_material_resolution_input,
    resolve_material_domain,
)
from visual_engine.runtime.domain_resolution import DomainResolutionStatus
from visual_engine.runtime.versioning import stable_digest


def _material(cid="m1", values=None, opacity=1.0):
    if values is None:
        values = (("name", "steel"), ("roughness", 0.35), ("metallic", 1.0))
    return AppearanceContribution(cid, AppearanceDomain.MATERIAL, "source", values, opacity=opacity)


def _input(contributions=(_material(),), **kwargs):
    return build_material_resolution_input(
        "helmet",
        contributions=contributions,
        dependencies={"appearance_layers": stable_digest("layers")},
        **kwargs,
    )


def test_single_opaque_material_contribution_resolves_all_declared_fields():
    result = resolve_material_domain(_input())
    assert result.status is DomainResolutionStatus.RESOLVED
    assert result.resolved_fields == (
        result.resolved_fields[0],
        result.resolved_fields[1],
        result.resolved_fields[2],
    )
    assert tuple(field.name for field in result.resolved_fields) == ("metallic", "name", "roughness")
    assert result.resolved_fields[0].value == 1.0
    assert result.resolved_fields[1].value == "steel"
    assert result.resolved_fields[2].value == 0.35


def test_resolver_identity_is_explicit_and_stable_by_default():
    data = _input()
    assert data.resolver_id == MATERIAL_RESOLVER_ID
    assert data.resolver_version == MATERIAL_RESOLVER_VERSION
    assert resolve_material_domain(data).result_digest == resolve_material_domain(data).result_digest


def test_partial_material_payload_is_preserved_without_inventing_defaults():
    result = resolve_material_domain(_input((_material(values=(("roughness", 0.25),)),)))
    assert result.status is DomainResolutionStatus.RESOLVED
    assert result.resolved_fields == (result.resolved_fields[0],)
    assert result.resolved_fields[0].name == "roughness"
    assert result.resolved_fields[0].value == 0.25


def test_empty_material_contribution_rejects_without_false_resolution():
    result = resolve_material_domain(_input((_material(values=()),)))
    assert result.status is DomainResolutionStatus.REJECTED
    assert result.resolved_fields == ()
    assert result.unresolved_reasons[0].startswith("MATERIAL_EMPTY_AUTHORITY:")


def test_zero_material_contributions_reject():
    result = resolve_material_domain(_input(()))
    assert result.status is DomainResolutionStatus.REJECTED
    assert result.unresolved_reasons[0].startswith("MATERIAL_NO_AUTHORITY:")


def test_multiple_material_contributions_reject_without_implicit_precedence():
    result = resolve_material_domain(_input((_material("m1"), _material("m2", (("roughness", 0.8),)))))
    assert result.status is DomainResolutionStatus.REJECTED
    assert result.unresolved_reasons[0].startswith("MATERIAL_MULTIPLE_AUTHORITIES:")


def test_translucent_material_contribution_rejects_without_underlay_semantics():
    result = resolve_material_domain(_input((_material(opacity=0.5),)))
    assert result.status is DomainResolutionStatus.REJECTED
    assert result.unresolved_reasons[0].startswith("MATERIAL_TRANSLUCENT_AUTHORITY:")


def test_values_are_not_averaged_summed_or_physically_transformed():
    material = _material(values=(("roughness", 0.0), ("metallic", 1.0), ("transmission", 0.75), ("emission", 0.75)))
    result = resolve_material_domain(_input((material,)))
    assert result.status is DomainResolutionStatus.RESOLVED
    assert dict((field.name, field.value) for field in result.resolved_fields) == {
        "roughness": 0.0,
        "metallic": 1.0,
        "transmission": 0.75,
        "emission": 0.75,
    }


def test_non_material_input_is_programming_error():
    data = build_material_resolution_input("helmet", contributions=(_material(),))
    object.__setattr__(data, "domain", AppearanceDomain.BASE)
    with pytest.raises(MaterialResolutionError):
        resolve_material_domain(data)
