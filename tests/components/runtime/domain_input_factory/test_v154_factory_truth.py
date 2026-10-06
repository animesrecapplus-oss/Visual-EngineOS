from visual_engine.runtime.domain_input_factory import build_domain_resolution_input
from visual_engine.runtime.domain_input_contract import DomainDependency, DomainResolutionInput
from visual_engine.runtime.domain_resolution import build_domain_resolution_input as legacy_build
from visual_engine.runtime import build_domain_resolution_input as public_build
from visual_engine.runtime.appearance_contract import AppearanceDomain


def test_factory_returns_canonical_input_owner():
    value = build_domain_resolution_input("x", AppearanceDomain.BASE)
    assert type(value) is DomainResolutionInput


def test_legacy_and_public_facades_share_factory_identity():
    assert legacy_build is build_domain_resolution_input
    assert public_build is build_domain_resolution_input


def test_dependency_mapping_is_canonicalized():
    value = build_domain_resolution_input(
        "x", AppearanceDomain.BASE, dependencies={"z": "a" * 64, "a": "b" * 64}
    )
    assert tuple(dep.name for dep in value.dependencies) == ("a", "z")


def test_invalid_dependency_item_is_rejected_by_canonical_contract():
    try:
        build_domain_resolution_input("x", AppearanceDomain.BASE, dependencies=(object(),))
    except (TypeError, AttributeError):
        pass
    else:
        raise AssertionError("invalid dependency item accepted")
