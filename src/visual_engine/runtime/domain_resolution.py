from __future__ import annotations

"""Domain-neutral resolver boundary for validated appearance domains.

This module intentionally stops one step before domain algorithms.  It defines
what a resolver may receive and what it may return, while keeping the actual
meaning of COLOR, MATERIAL, LIGHTING, etc. owned by their respective contracts.

The boundary is deliberately fail-closed:
- one input targets exactly one rendering domain;
- every contribution must belong to that domain and satisfy its existing contract;
- output fields must belong to the same domain contract;
- provenance and dependency digests are mandatory for resolved output;
- this layer never mixes, clamps, converts, shades or mutates values.
"""

from typing import Mapping, TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from visual_engine.runtime.appearance_role_bridge import AppearanceRoleContribution

from visual_engine.runtime.versioning import stable_digest
from visual_engine.runtime.domain_result_contract import (
    DomainResolutionStatus,
    DomainResolvedField,
    DomainResolutionProvenance,
    DomainResolutionResult,
    _require_rendering_domain,
    _validate_digest,
)
from visual_engine.runtime.domain_result_validation import validate_domain_resolution_result  # V1.51: compatibility facade preserves the historical public import.






# V1.53 compatibility surface: the input contract has one canonical owner.
from visual_engine.runtime.domain_input_contract import DomainDependency, DomainResolutionInput


from visual_engine.runtime.domain_input_factory import build_domain_resolution_input
def unresolved_domain_result(input_data: DomainResolutionInput, reason: str) -> DomainResolutionResult:
    """Create an explicit no-algorithm-yet result without pretending resolution occurred."""
    if not reason:
        raise ValueError("unresolved reason must not be empty")
    return DomainResolutionResult(
        target_id=input_data.target_id,
        domain=input_data.domain,
        status=DomainResolutionStatus.UNRESOLVED,
        input_digest=input_data.input_digest,
        resolver_id=input_data.resolver_id,
        resolver_version=input_data.resolver_version,
        unresolved_reasons=(reason,),
        dependency_digest=stable_digest(input_data.dependencies),
    )


