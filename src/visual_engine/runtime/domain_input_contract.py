from __future__ import annotations

"""Immutable renderer-neutral input contract for one appearance domain.

This module owns the semantic input envelope and its dependency value object.
Construction helpers remain in ``domain_resolution`` so the factory remains the
legacy compatibility boundary; no domain algorithm or result validation lives here.
"""

from dataclasses import dataclass
from typing import TYPE_CHECKING

from visual_engine.runtime.appearance_contract import (
    AppearanceContribution,
    AppearanceDomain,
    DomainContractError,
    validate_appearance_contributions,
)
from visual_engine.runtime.domain_result_contract import _require_rendering_domain, _validate_digest
from visual_engine.runtime.versioning import stable_digest

if TYPE_CHECKING:  # pragma: no cover
    from visual_engine.runtime.appearance_role_bridge import AppearanceRoleContribution


@dataclass(frozen=True, slots=True)
class DomainDependency:
    """Name plus deterministic content identity of an upstream dependency."""

    name: str
    digest: str

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise ValueError("domain dependency name must not be empty")
        _validate_digest(self.digest, "domain dependency digest")


@dataclass(frozen=True, slots=True)
class DomainResolutionInput:
    """Immutable input envelope for exactly one renderer appearance domain."""

    target_id: str
    domain: AppearanceDomain
    contributions: tuple[AppearanceContribution, ...] = ()
    active_states: tuple[str, ...] = ()
    dependencies: tuple[DomainDependency, ...] = ()
    resolver_id: str = "unresolved"
    resolver_version: str = "contract-only"
    contract_version: str = "1"
    role_contribution: "AppearanceRoleContribution | None" = None

    def __post_init__(self) -> None:
        # Input identity is immutable because it participates in resolver fingerprints.
        if not isinstance(self.target_id, str) or not self.target_id:
            raise ValueError("domain resolution target_id must not be empty")
        if not isinstance(self.domain, AppearanceDomain):
            raise TypeError("domain must be an AppearanceDomain")
        _require_rendering_domain(self.domain)
        if (
            not isinstance(self.resolver_id, str)
            or not self.resolver_id
            or not isinstance(self.resolver_version, str)
            or not self.resolver_version
            or not isinstance(self.contract_version, str)
            or not self.contract_version
        ):
            raise ValueError("domain resolver/version identifiers are required")
        if any(not isinstance(state, str) or not state for state in self.active_states):
            raise ValueError("active state names must be non-empty strings")
        if tuple(sorted(set(self.active_states))) != self.active_states:
            raise ValueError("active_states must be canonicalized")
        if any(not isinstance(item, AppearanceContribution) for item in self.contributions):
            raise TypeError("domain resolution contributions must contain AppearanceContribution instances")
        if len({item.contribution_id for item in self.contributions}) != len(self.contributions):
            raise ValueError("domain resolution contribution IDs must be unique")
        if self.role_contribution is not None:
            from visual_engine.runtime.appearance_role_bridge import AppearanceRoleContribution
            if not isinstance(self.role_contribution, AppearanceRoleContribution):
                raise TypeError("role_contribution must be AppearanceRoleContribution")
            if self.role_contribution.target_id != self.target_id:
                raise ValueError("role contribution target does not match domain input")
            if self.domain not in {AppearanceDomain.BASE, AppearanceDomain.COLOR}:
                raise DomainContractError(
                    "typed role contribution is authoritative only for BASE and COLOR domain resolution"
                )
            if any(item.domain is self.domain for item in self.contributions):
                raise DomainContractError(
                    f"typed role contribution cannot coexist with a legacy {self.domain.value.upper()} contribution"
                )
        if any(item.domain is not self.domain for item in self.contributions):
            raise DomainContractError(
                f"domain resolution input for '{self.domain.value}' cannot contain another domain"
            )
        validate_appearance_contributions(self.contributions)
        if any(not isinstance(item, DomainDependency) for item in self.dependencies):
            raise TypeError("domain dependencies must contain DomainDependency instances")
        if tuple(sorted(self.dependencies, key=lambda item: item.name)) != self.dependencies:
            raise ValueError("domain dependencies must be sorted by name")
        if len({item.name for item in self.dependencies}) != len(self.dependencies):
            raise ValueError("domain dependency names must be unique")

    @property
    def input_digest(self) -> str:
        """Return the canonical SHA-256 identity of the complete input envelope."""
        return stable_digest(self)
