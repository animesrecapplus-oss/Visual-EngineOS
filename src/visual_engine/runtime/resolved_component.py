from __future__ import annotations

"""Canonical immutable result contract produced by runtime resolution.

This module owns the value envelope only. Resolution policy, cache policy,
fingerprint construction and provenance generation remain external owners.
"""

from dataclasses import dataclass

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.visual_contract import ResolvedVisualContract
from visual_engine.runtime.provenance import ResolutionProvenance
from visual_engine.runtime.versioning import ResolutionFingerprint, VersionStamp


@dataclass(frozen=True, slots=True)
class ResolutionTrace:
    """Minimal deterministic legacy trace carried by a resolved result."""

    entries: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ResolvedComponent:
    """Renderer-neutral immutable envelope for one resolved component."""

    component_id: str
    kind: str
    visual: ResolvedVisualContract
    geometry: GeometryContract
    trace: ResolutionTrace = ResolutionTrace()
    provenance: ResolutionProvenance = ResolutionProvenance()
    version: VersionStamp = VersionStamp()
    fingerprint: ResolutionFingerprint | None = None
