from __future__ import annotations

"""V1.27 renderer-neutral BASE + Palette composition boundary.

Composition here means deterministic *selection*, not color mixing.  BASE and
Palette remain separate authorities and their provenance is preserved.  No
alpha compositing, shading, lighting, material response, or style transform is
performed by this module.
"""

from dataclasses import dataclass
from enum import Enum

from visual_engine.components.common.base_color import BaseColor, BaseColorRole
from visual_engine.components.common.palette import PaletteEntry, PaletteSlot
from visual_engine.runtime.base_color_resolution import resolve_base_color
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.identity import stable_digest
from visual_engine.runtime.palette_resolution import resolve_palette

APPEARANCE_COMPOSITION_VERSION = "1"


class AppearanceCompositionError(ValueError):
    """Raised when a composition request is contradictory or malformed."""


class CompositionMode(str, Enum):
    BASE_ONLY = "base-only"
    PALETTE_ONLY = "palette-only"
    BASE_THEN_PALETTE = "base-then-palette"
    PALETTE_THEN_BASE = "palette-then-base"
    REJECT_SAME_ROLE = "reject-same-role"


class CompositionSource(str, Enum):
    BASE = "base"
    PALETTE = "palette"
    NONE = "none"


@dataclass(frozen=True, slots=True)
class AppearanceCompositionRequest:
    role: BaseColorRole
    mode: CompositionMode = CompositionMode.BASE_THEN_PALETTE
    require_base: bool = False
    require_palette: bool = False

    def __post_init__(self) -> None:
        if not isinstance(self.role, BaseColorRole):
            raise AppearanceCompositionError("composition role must be a BaseColorRole")
        if not isinstance(self.mode, CompositionMode):
            raise AppearanceCompositionError("composition mode must be a CompositionMode")
        if not isinstance(self.require_base, bool) or not isinstance(self.require_palette, bool):
            raise AppearanceCompositionError("composition requirements must be boolean")
        if self.mode is CompositionMode.BASE_ONLY and self.require_palette:
            raise AppearanceCompositionError("BASE_ONLY cannot require a palette")
        if self.mode is CompositionMode.PALETTE_ONLY and self.require_base:
            raise AppearanceCompositionError("PALETTE_ONLY cannot require BASE")


@dataclass(frozen=True, slots=True)
class AppearanceCompositionProvenance:
    base_fingerprint: str | None
    base_authority_component_id: str | None
    palette_fingerprint: str | None
    palette_authority_component_id: str | None
    selected_source: CompositionSource
    selected_slot: PaletteSlot | None
    base_source_id: str | None = None
    base_lineage: tuple[str, ...] = ()
    palette_source_id: str | None = None
    palette_lineage: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class AppearanceComposition:
    target_component_id: str
    request: AppearanceCompositionRequest
    base_color: BaseColor | None
    palette_entry: PaletteEntry | None
    selected_color: object | None
    provenance: AppearanceCompositionProvenance
    status: str
    reason: str
    fingerprint: str

    def __post_init__(self) -> None:
        if self.status not in {"resolved", "unresolved", "rejected"}:
            raise ValueError("unsupported appearance composition status")
        if self.status == "resolved" and self.selected_color is None:
            raise ValueError("resolved composition requires a selected color")
        if self.status != "resolved" and self.selected_color is not None:
            raise ValueError("non-resolved composition cannot carry a selected color")
        if len(self.fingerprint) != 64:
            raise ValueError("composition fingerprint must be SHA-256")


def _composition_fingerprint(
    target_component_id: str,
    request: AppearanceCompositionRequest,
    base_resolution,
    palette_resolution,
) -> str:
    """Hash only composition inputs; geometry/transform/material are absent."""
    return stable_digest({
        "version": APPEARANCE_COMPOSITION_VERSION,
        "target": target_component_id,
        "request": request,
        "base": None if base_resolution.color is None else base_resolution.color.fingerprint,
        "base_dependency": base_resolution.dependency_fingerprint,
        "palette": None if palette_resolution.palette is None else palette_resolution.palette.fingerprint,
        "palette_dependency": palette_resolution.dependency_fingerprint,
        "palette_slot": None if palette_resolution.selected_slot is None else palette_resolution.selected_slot.value,
    })


def appearance_composition_fingerprint(graph: RuntimeGraph, component_id: str, request: AppearanceCompositionRequest) -> str:
    """Return the targeted composition identity before selecting a result."""
    base = resolve_base_color(graph, component_id)
    palette = resolve_palette(graph, component_id, slot=_role_to_slot(request.role))
    return _composition_fingerprint(component_id, request, base, palette)


def _role_to_slot(role: BaseColorRole) -> PaletteSlot:
    try:
        return PaletteSlot(role.value)
    except ValueError as exc:
        # BACKGROUND/CUSTOM have no palette slot in V1.27.  They must not silently
        # map to primary because that would create a hidden semantic fallback.
        raise AppearanceCompositionError(
            f"BaseColor role '{role.value}' has no V1.27 palette slot"
        ) from exc


def _resolve_base(graph: RuntimeGraph, component_id: str, role: BaseColorRole):
    result = resolve_base_color(graph, component_id)
    if result.status == "resolved" and result.color is not None and result.color.role is not role:
        return result.__class__(component_id, None, "unresolved", f"resolved BASE role is '{result.color.role.value}', requested '{role.value}'", result.dependency_fingerprint)
    return result


def resolve_appearance_composition(
    graph: RuntimeGraph,
    component_id: str,
    request: AppearanceCompositionRequest,
) -> AppearanceComposition:
    """Resolve one semantic role without creating a hidden third color authority."""
    slot = _role_to_slot(request.role)
    base = _resolve_base(graph, component_id, request.role)
    palette = resolve_palette(graph, component_id, slot=slot)
    fingerprint = _composition_fingerprint(component_id, request, base, palette)

    base_value = base.color if base.status == "resolved" else None
    palette_value = palette.selected_entry if palette.status == "resolved" else None

    if request.require_base and base_value is None:
        return AppearanceComposition(
            component_id, request, None, None, None,
            AppearanceCompositionProvenance(None, None, None, None, CompositionSource.NONE, None),
            "unresolved", "required BASE role is unavailable", fingerprint,
        )
    if request.require_palette and palette_value is None:
        return AppearanceComposition(
            component_id, request, None, None, None,
            AppearanceCompositionProvenance(None, None, None, None, CompositionSource.NONE, None),
            "unresolved", "required palette slot is unavailable", fingerprint,
        )

    if request.mode is CompositionMode.BASE_ONLY:
        if base_value is None:
            return AppearanceComposition(component_id, request, None, None, None, AppearanceCompositionProvenance(None, None, None, None, CompositionSource.NONE, None), "unresolved", "BASE_ONLY has no matching BASE authority", fingerprint)
        return _resolved(component_id, request, base_value, None, CompositionSource.BASE, base, palette, fingerprint)

    if request.mode is CompositionMode.PALETTE_ONLY:
        if palette_value is None:
            return AppearanceComposition(component_id, request, None, None, None, AppearanceCompositionProvenance(None, None, None, None, CompositionSource.NONE, None), "unresolved", "PALETTE_ONLY has no requested palette slot", fingerprint)
        return _resolved(component_id, request, None, palette_value, CompositionSource.PALETTE, base, palette, fingerprint)

    if request.mode is CompositionMode.REJECT_SAME_ROLE and base_value is not None and palette_value is not None:
        return AppearanceComposition(component_id, request, base_value, palette_value, None, AppearanceCompositionProvenance(base_value.fingerprint, base_value.provenance.authority_component_id, palette.palette.fingerprint, palette.palette.provenance.authority_component_id, CompositionSource.NONE, slot), "rejected", "BASE and Palette both claim the requested semantic role", fingerprint)

    if request.mode is CompositionMode.BASE_THEN_PALETTE:
        if base_value is not None:
            return _resolved(component_id, request, base_value, palette_value, CompositionSource.BASE, base, palette, fingerprint)
        if palette_value is not None:
            return _resolved(component_id, request, None, palette_value, CompositionSource.PALETTE, base, palette, fingerprint)
    elif request.mode is CompositionMode.PALETTE_THEN_BASE:
        if palette_value is not None:
            return _resolved(component_id, request, base_value, palette_value, CompositionSource.PALETTE, base, palette, fingerprint)
        if base_value is not None:
            return _resolved(component_id, request, base_value, None, CompositionSource.BASE, base, palette, fingerprint)

    return AppearanceComposition(component_id, request, None, None, None, AppearanceCompositionProvenance(None, None, None, None, CompositionSource.NONE, None), "unresolved", "no BASE or palette value satisfies the composition request", fingerprint)


def _resolved(component_id, request, base_value, palette_value, source, base, palette, fingerprint):
    provenance = AppearanceCompositionProvenance(
        None if base_value is None else base_value.fingerprint,
        None if base_value is None else base_value.provenance.authority_component_id,
        None if palette.palette is None else palette.palette.fingerprint,
        None if palette.palette is None else palette.palette.provenance.authority_component_id,
        source,
        palette.selected_slot,
        None if base_value is None else base_value.provenance.source_id,
        () if base_value is None else base_value.provenance.lineage,
        None if palette.palette is None else palette.palette.provenance.source_id,
        () if palette.palette is None else palette.palette.provenance.lineage,
    )
    return AppearanceComposition(component_id, request, base_value, palette_value, base_value if source is CompositionSource.BASE else palette_value, provenance, "resolved", "deterministic source selection; no color compositing", fingerprint)
