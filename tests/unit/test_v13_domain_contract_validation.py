import pytest

from visual_engine.components.common.visual_contract import ContourContract, MaterialContract
from visual_engine.runtime.appearance_contract import (
    AppearanceContribution,
    AppearanceDomain,
    DomainContractError,
    DOMAIN_CONTRACTS,
    build_appearance_input,
    resolve_appearance_contract,
    validate_appearance_contribution,
)


def c(domain, values):
    return AppearanceContribution(f"x-{domain.value}", domain, "source", tuple(values.items()))


def test_all_seven_render_domains_have_explicit_closed_contracts():
    expected = {
        AppearanceDomain.BASE,
        AppearanceDomain.MATERIAL,
        AppearanceDomain.COLOR,
        AppearanceDomain.LIGHTING,
        AppearanceDomain.TRANSMISSION,
        AppearanceDomain.REFLECTION,
        AppearanceDomain.EMISSION,
    }
    assert set(DOMAIN_CONTRACTS) == expected
    assert all(contract.field_map for contract in DOMAIN_CONTRACTS.values())


def test_base_requires_base_color_and_rejects_unknown_semantics():
    validate_appearance_contribution(c(AppearanceDomain.BASE, {"base_color": "#ffffff"}))
    with pytest.raises(DomainContractError, match="requires fields"):
        validate_appearance_contribution(c(AppearanceDomain.BASE, {}))
    with pytest.raises(DomainContractError, match="does not declare fields"):
        validate_appearance_contribution(c(AppearanceDomain.BASE, {"color": "#fff"}))


def test_material_uses_existing_material_contract_vocabulary():
    validate_appearance_contribution(c(AppearanceDomain.MATERIAL, {"roughness": .2, "metallic": .7}))
    with pytest.raises(DomainContractError, match=r"\[0,1\]"):
        validate_appearance_contribution(c(AppearanceDomain.MATERIAL, {"roughness": 1.2}))


def test_color_is_not_allowed_to_smuggle_material_or_lighting_fields():
    validate_appearance_contribution(c(AppearanceDomain.COLOR, {"pattern": "procedural", "saturation": .4}))
    with pytest.raises(DomainContractError, match="does not declare fields"):
        validate_appearance_contribution(c(AppearanceDomain.COLOR, {"roughness": .2}))


def test_lighting_accepts_typed_channels_without_applying_lighting():
    validate_appearance_contribution(c(AppearanceDomain.LIGHTING, {"color": "#ffffff", "intensity": 2.0, "direction": (1.0, 0.0)}))
    with pytest.raises(DomainContractError, match="must be >= 0"):
        validate_appearance_contribution(c(AppearanceDomain.LIGHTING, {"intensity": -1}))


def test_transmission_has_explicit_physical_parameter_boundaries():
    validate_appearance_contribution(c(AppearanceDomain.TRANSMISSION, {"amount": .5, "ior": 1.5, "thickness": 2.0}))
    with pytest.raises(DomainContractError, match=">= 1.0"):
        validate_appearance_contribution(c(AppearanceDomain.TRANSMISSION, {"ior": .9}))


def test_reflection_strength_example_from_previous_contract_is_valid():
    validate_appearance_contribution(c(AppearanceDomain.REFLECTION, {"strength": .5}))
    with pytest.raises(DomainContractError, match=r"\[0,1\]"):
        validate_appearance_contribution(c(AppearanceDomain.REFLECTION, {"strength": 2}))


def test_emission_is_separate_from_lighting_and_has_no_algorithm():
    validate_appearance_contribution(c(AppearanceDomain.EMISSION, {"color": "#ffcc00", "intensity": 3.0}))
    with pytest.raises(DomainContractError, match="does not declare fields"):
        validate_appearance_contribution(c(AppearanceDomain.EMISSION, {"roughness": .2}))


def test_contract_validation_happens_at_appearance_resolution_boundary():
    data = build_appearance_input(
        "eye", base_color="#ffffff", contour=ContourContract(), material=MaterialContract(),
        opacity=1, visibility=1,
        contributions=(c(AppearanceDomain.COLOR, {"unknown": 1}),),
    )
    with pytest.raises(DomainContractError):
        resolve_appearance_contract(data)


def test_validation_does_not_mutate_or_normalize_payload():
    contribution = c(AppearanceDomain.COLOR, {"pattern": "procedural", "saturation": 0.25})
    before = contribution.values
    validate_appearance_contribution(contribution)
    assert contribution.values == before
