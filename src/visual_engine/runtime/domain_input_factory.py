from __future__ import annotations

"""Canonical construction boundary for domain-resolution inputs.

This module owns normalization only: it never resolves a domain and never
constructs a domain-resolution result. The immutable value objects remain in
``domain_input_contract``; this factory is their single construction policy.
"""

from typing import Mapping

from visual_engine.runtime.appearance_contract import (
    AppearanceContribution,
    AppearanceDomain,
    DomainContractError,
)
from visual_engine.runtime.domain_input_contract import DomainDependency, DomainResolutionInput
from visual_engine.runtime.domain_result_contract import _require_rendering_domain


def build_domain_resolution_input(
    target_id: str,
    domain: AppearanceDomain,
    *,
    contributions: tuple[AppearanceContribution, ...] = (),
    active_states: tuple[str, ...] = (),
    dependencies: Mapping[str, str] | tuple[DomainDependency, ...] = (),
    resolver_id: str = "unresolved",
    resolver_version: str = "contract-only",
    contract_version: str = "1",
    role_contribution=None,
) -> DomainResolutionInput:
    """Build the canonical immutable input without applying domain semantics."""
    _require_rendering_domain(domain)
    if isinstance(dependencies, Mapping):
        dependency_items = tuple(
            DomainDependency(name, digest) for name, digest in sorted(dependencies.items())
        )
    else:
        raw_dependencies = tuple(dependencies)
        if any(not isinstance(item, DomainDependency) for item in raw_dependencies):
            raise TypeError("dependencies must contain only DomainDependency values")
        dependency_items = tuple(sorted(raw_dependencies, key=lambda item: item.name))
    if role_contribution is not None:
        from visual_engine.runtime.appearance_role_bridge import AppearanceRoleContribution
        if not isinstance(role_contribution, AppearanceRoleContribution):
            raise TypeError("role_contribution must be AppearanceRoleContribution")
        role_dependency = DomainDependency("appearance_role_bridge", role_contribution.fingerprint)
        existing = next((item for item in dependency_items if item.name == role_dependency.name), None)
        if existing is not None and existing.digest != role_dependency.digest:
            raise DomainContractError("appearance_role_bridge dependency contradicts typed role contribution")
        if existing is None:
            dependency_items = tuple(sorted((*dependency_items, role_dependency), key=lambda item: item.name))
    return DomainResolutionInput(
        target_id=target_id,
        domain=domain,
        contributions=tuple(contributions),
        active_states=tuple(sorted(set(active_states))),
        dependencies=dependency_items,
        resolver_id=resolver_id,
        resolver_version=resolver_version,
        contract_version=contract_version,
        role_contribution=role_contribution,
    )
