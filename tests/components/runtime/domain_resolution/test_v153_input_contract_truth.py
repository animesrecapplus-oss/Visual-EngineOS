from __future__ import annotations

from visual_engine.runtime import DomainDependency, DomainResolutionInput
from visual_engine.runtime.appearance_contract import AppearanceContribution, AppearanceDomain
from visual_engine.runtime.domain_input_contract import (
    DomainDependency as CanonicalDependency,
    DomainResolutionInput as CanonicalInput,
)
from visual_engine.runtime.domain_resolution import build_domain_resolution_input
from visual_engine.runtime.versioning import stable_digest


def _contribution():
    return AppearanceContribution("c1", AppearanceDomain.COLOR, "source", (("saturation", 0.2),))


def _input(**kwargs):
    return build_domain_resolution_input(
        "eye",
        AppearanceDomain.COLOR,
        contributions=(_contribution(),),
        resolver_id="color.test",
        resolver_version="1",
        **kwargs,
    )


def test_input_types_have_one_canonical_owner_and_legacy_identity():
    assert DomainResolutionInput is CanonicalInput
    assert DomainDependency is CanonicalDependency


def test_input_digest_is_deterministic_and_geometry_independent():
    first = _input()
    second = _input()
    assert first.input_digest == second.input_digest
    changed = build_domain_resolution_input(
        "eye", AppearanceDomain.COLOR, contributions=(_contribution(),),
        dependencies={"visual_only": stable_digest("one")},
        resolver_id="color.test", resolver_version="1",
    )
    assert changed.input_digest != first.input_digest


def test_input_rejects_hostile_runtime_types():
    digest = stable_digest("dependency")
    cases = [
        {"target_id": None},
        {"domain": "color"},
        {"contributions": (object(),)},
        {"active_states": ("ok", 1)},
        {"dependencies": (object(),)},
        {"resolver_id": None},
        {"resolver_version": 1},
        {"contract_version": 2},
    ]
    for overrides in cases:
        values = dict(target_id="eye", domain=AppearanceDomain.COLOR)
        values.update(overrides)
        if "dependencies" not in values:
            values["dependencies"] = (CanonicalDependency("d", digest),)
        try:
            CanonicalInput(**values)
        except (TypeError, ValueError):
            pass
        else:
            raise AssertionError(f"hostile input accepted: {overrides}")


def test_input_rejects_noncanonical_states_and_dependency_order():
    contribution = _contribution()
    digest = stable_digest("dependency")
    for states, dependencies in [
        (("z", "a"), ()),
        ((), (CanonicalDependency("z", digest), CanonicalDependency("a", digest))),
    ]:
        try:
            CanonicalInput(
                "eye", AppearanceDomain.COLOR, (contribution,), states, dependencies,
                "r", "1", "1", None,
            )
        except ValueError:
            pass
        else:
            raise AssertionError("non-canonical input accepted")


def test_input_rejects_duplicate_or_cross_domain_contributions():
    digest = stable_digest("dependency")
    duplicate = _contribution()
    for contributions in (
        (duplicate, duplicate),
        (duplicate, AppearanceContribution("c2", AppearanceDomain.MATERIAL, "source", (("name", "x"),))),
    ):
        try:
            CanonicalInput(
                "eye", AppearanceDomain.COLOR, contributions, (),
                (CanonicalDependency("d", digest),), "r", "1", "1", None,
            )
        except (TypeError, ValueError):
            pass
        else:
            raise AssertionError("invalid contribution set accepted")
