from __future__ import annotations

"""Immutable result-side contract for appearance-domain resolution."""

from dataclasses import dataclass
from enum import Enum
from typing import Any

from visual_engine.runtime.appearance_contract import AppearanceDomain, DomainContractError
from visual_engine.runtime.versioning import stable_digest

_RENDERING_DOMAINS = frozenset({
    AppearanceDomain.BASE, AppearanceDomain.MATERIAL, AppearanceDomain.COLOR,
    AppearanceDomain.LIGHTING, AppearanceDomain.TRANSMISSION,
    AppearanceDomain.REFLECTION, AppearanceDomain.EMISSION,
})

class DomainResolutionStatus(str, Enum):
    """Lifecycle state of one domain-resolution attempt."""

    UNRESOLVED = "unresolved"
    RESOLVED = "resolved"
    PARTIAL = "partial"
    REJECTED = "rejected"

@dataclass(frozen=True, slots=True)
class DomainResolvedField:
    """One produced field; its value remains subject to the domain contract."""

    name: str
    value: Any

    def __post_init__(self) -> None:
        if not isinstance(self.name, str) or not self.name:
            raise TypeError("resolved field name must be a non-empty string")


@dataclass(frozen=True, slots=True)
class DomainResolutionProvenance:
    """Deterministic lineage attached to a domain-resolution result."""

    target_id: str
    domain: AppearanceDomain
    contribution_ids: tuple[str, ...]
    dependency_names: tuple[str, ...]
    resolver_id: str
    resolver_version: str
    role_bridge_fingerprint: str | None = None
    role_authority_component_id: str | None = None
    role_source_id: str | None = None
    role_lineage: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not all(isinstance(value, str) and value for value in (self.target_id, self.resolver_id, self.resolver_version)):
            raise TypeError("domain provenance identifiers must be non-empty strings")
        if not isinstance(self.domain, AppearanceDomain):
            raise TypeError("domain provenance domain must be an AppearanceDomain")
        if any(not isinstance(value, str) or not value for value in (*self.contribution_ids, *self.dependency_names)):
            raise TypeError("provenance IDs and dependency names must be non-empty strings")
        if any(not isinstance(value, str) or not value for value in (*((self.role_authority_component_id, self.role_source_id) if self.role_bridge_fingerprint is not None else ()), *self.role_lineage)):
            raise TypeError("role provenance IDs and lineage values must be non-empty strings")
        if self.domain not in _RENDERING_DOMAINS:
            raise ValueError("domain provenance must reference a rendering appearance domain")
        if tuple(sorted(set(self.contribution_ids))) != self.contribution_ids:
            raise ValueError("provenance contribution IDs must be sorted and unique")
        if tuple(sorted(set(self.dependency_names))) != self.dependency_names:
            raise ValueError("provenance dependency names must be sorted and unique")
        if self.role_bridge_fingerprint is not None:
            _validate_digest(self.role_bridge_fingerprint, "role bridge fingerprint")
            if not self.role_authority_component_id or not self.role_source_id:
                raise ValueError("role bridge provenance requires authority and source IDs")
            if not self.role_lineage or self.role_lineage[-1] != self.target_id:
                raise ValueError("role bridge provenance lineage must terminate at target")
        elif any((self.role_authority_component_id, self.role_source_id, self.role_lineage)):
            raise ValueError("role bridge provenance fields require a role bridge fingerprint")

    @property
    def digest(self) -> str:
        """Stable provenance identity independent of object identity."""
        return stable_digest(self)


@dataclass(frozen=True, slots=True)
class DomainResolutionResult:
    """Immutable output envelope; no resolver algorithm is executed here."""

    target_id: str
    domain: AppearanceDomain
    status: DomainResolutionStatus
    input_digest: str
    resolver_id: str
    resolver_version: str
    resolved_fields: tuple[DomainResolvedField, ...] = ()
    unresolved_reasons: tuple[str, ...] = ()
    provenance: DomainResolutionProvenance | None = None
    dependency_digest: str = ""

    def __post_init__(self) -> None:
        if not all(isinstance(value, str) and value for value in (self.target_id, self.resolver_id, self.resolver_version)):
            raise TypeError("domain result identifiers must be non-empty strings")
        if not isinstance(self.domain, AppearanceDomain):
            raise TypeError("domain result domain must be an AppearanceDomain")
        if not isinstance(self.status, DomainResolutionStatus):
            raise TypeError("domain result status must be a DomainResolutionStatus")
        if not isinstance(self.resolved_fields, tuple) or any(not isinstance(field, DomainResolvedField) for field in self.resolved_fields):
            raise TypeError("resolved_fields must be a tuple of DomainResolvedField")
        if not isinstance(self.unresolved_reasons, tuple):
            raise TypeError("unresolved_reasons must be a tuple")
        if self.provenance is not None and not isinstance(self.provenance, DomainResolutionProvenance):
            raise TypeError("provenance must be DomainResolutionProvenance or None")
        _require_rendering_domain(self.domain)
        _validate_digest(self.input_digest, "domain result input digest")
        _validate_digest(self.dependency_digest, "domain result dependency digest")
        if any(not isinstance(reason, str) or not reason for reason in self.unresolved_reasons):
            raise ValueError("unresolved reasons must be non-empty strings")
        if self.status in {DomainResolutionStatus.UNRESOLVED, DomainResolutionStatus.PARTIAL, DomainResolutionStatus.REJECTED} and not self.unresolved_reasons:
            raise ValueError(f"{self.status.value} domain results require explicit unresolved reasons")
        names = [field.name for field in self.resolved_fields]
        if len(names) != len(set(names)):
            raise ValueError("resolved field names must be unique")
        if tuple(sorted(names)) != tuple(names):
            raise ValueError("resolved fields must be sorted by name")
        if self.status in {DomainResolutionStatus.UNRESOLVED, DomainResolutionStatus.REJECTED} and self.resolved_fields:
            raise ValueError(f"{self.status.value} domain results cannot contain resolved fields")
        if self.status is DomainResolutionStatus.RESOLVED and self.unresolved_reasons:
            raise ValueError("resolved domain results cannot contain unresolved reasons")
        if self.status in {DomainResolutionStatus.RESOLVED, DomainResolutionStatus.PARTIAL} and self.provenance is None:
            raise ValueError("resolved/partial domain results require provenance")
        if self.provenance is not None:
            if self.provenance.target_id != self.target_id or self.provenance.domain is not self.domain:
                raise ValueError("domain result provenance does not match target/domain")
            if self.provenance.resolver_id != self.resolver_id or self.provenance.resolver_version != self.resolver_version:
                raise ValueError("domain result provenance does not match resolver identity")

    @property
    def result_digest(self) -> str:
        """Stable identity of the complete immutable result envelope."""
        return stable_digest(self)


def _require_rendering_domain(domain: AppearanceDomain) -> None:
    # Shared contract primitive: input and result envelopes must admit only renderable domains.
    if domain not in _RENDERING_DOMAINS:
        raise DomainContractError(f"domain '{domain.value}' is not a rendering appearance domain")


def _validate_digest(value: str, label: str) -> None:
    # Structural digest guard; stable_digest remains the canonical identity generator.
    if not isinstance(value, str) or len(value) != 64 or any(c not in "0123456789abcdef" for c in value.lower()):
        raise ValueError(f"{label} must be a SHA-256 hexadecimal digest")
