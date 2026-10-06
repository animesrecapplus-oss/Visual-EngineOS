from __future__ import annotations

"""Targeted resolution of the V1.26 whole-palette authority.

The resolver chooses one palette authority first, then looks up one semantic slot
inside that authority. It never merges slots from different ancestors. This is a
critical invariant consumed by V1.27 appearance composition.
"""

from dataclasses import dataclass

from visual_engine.components.common.base_color import BaseColorError
from visual_engine.components.common.meta import Component
from visual_engine.components.common.palette import (
    Palette,
    PaletteError,
    PaletteOverridePolicy,
    PaletteSlot,
)
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.identity import stable_digest

PALETTE_RESOLUTION_VERSION = "1"


@dataclass(frozen=True, slots=True)
class PaletteResolution:
    target_component_id: str
    palette: Palette | None
    selected_slot: PaletteSlot | None
    selected_entry: object | None
    status: str
    reason: str = ""
    dependency_fingerprint: str = ""

    def __post_init__(self) -> None:
        if self.status not in {"resolved", "unresolved", "rejected"}:
            raise ValueError("unsupported palette resolution status")
        if self.status == "resolved" and self.palette is None:
            raise ValueError("resolved palette requires an authority")
        if self.status == "resolved" and self.selected_slot is not None and self.selected_entry is None:
            raise ValueError("resolved palette slot requires an entry")
        if self.status != "resolved" and (self.palette is not None or self.selected_entry is not None):
            raise ValueError("non-resolved palette result cannot carry resolved authority data")
        if self.status != "resolved" and not self.reason:
            raise ValueError("non-resolved palette result requires a reason")
        if len(self.dependency_fingerprint) != 64:
            raise ValueError("palette dependency fingerprint must be SHA-256")


def _ancestors_nearest_first(graph: RuntimeGraph, component_id: str) -> tuple[Component, ...]:
    current = graph.get(component_id)
    result: list[Component] = []
    while current.parent_id is not None:
        current = graph.get(current.parent_id)
        result.append(current.component)
    return tuple(result)


def _validate_legacy_contradiction(component: Component) -> None:
    legacy = [layer for layer in component.appearance if "palette" in layer.values]
    if component.palette is not None and legacy:
        raise PaletteError(f"component {component.id!r} has typed palette and legacy palette authority")
    if len(legacy) > 1:
        raise PaletteError(f"component {component.id!r} has multiple legacy palette authorities")


def _nearest_palette(graph: RuntimeGraph, component_id: str) -> Component | None:
    return next((c for c in _ancestors_nearest_first(graph, component_id) if c.palette is not None), None)


def _palette_dependency_payload(graph: RuntimeGraph, component_id: str) -> dict:
    component = graph.get(component_id).component
    local = component.palette
    nearest = _nearest_palette(graph, component_id)
    chain: list[dict] = [{"id": component_id, "palette": local}]
    if local is None:
        if nearest is not None:
            chain.append({"id": nearest.id, "palette": nearest.palette})
    elif nearest is not None:
        policy = nearest.palette.inheritance.override_policy
        if policy is not PaletteOverridePolicy.LOCAL_WINS and nearest.palette.inheritance.allow_children:
            chain.append({"id": nearest.id, "palette": nearest.palette})
    return {"version": PALETTE_RESOLUTION_VERSION, "target": component_id, "hierarchy": chain}


def palette_resolution_fingerprint(graph: RuntimeGraph, component_id: str) -> str:
    """Fingerprint only palette authorities relevant to this target."""
    return stable_digest(_palette_dependency_payload(graph, component_id))


def resolve_palette(
    graph: RuntimeGraph,
    component_id: str,
    *,
    slot: PaletteSlot | None = None,
) -> PaletteResolution:
    """Resolve one whole-palette authority and optionally one slot."""
    component = graph.get(component_id).component
    _validate_legacy_contradiction(component)
    for ancestor in _ancestors_nearest_first(graph, component_id):
        _validate_legacy_contradiction(ancestor)

    fingerprint = palette_resolution_fingerprint(graph, component_id)
    local = component.palette
    nearest = _nearest_palette(graph, component_id)

    if local is not None:
        if nearest is None or nearest.palette.inheritance.override_policy is PaletteOverridePolicy.LOCAL_WINS:
            authority = local
        elif nearest.palette.inheritance.override_policy is PaletteOverridePolicy.INHERIT_WINS and nearest.palette.inheritance.allow_children:
            hierarchy = list(reversed(_ancestors_nearest_first(graph, component_id)))
            start = next(i for i, item in enumerate(hierarchy) if item.id == nearest.id)
            lineage = tuple(item.id for item in hierarchy[start:] + [component])
            authority = nearest.palette.inherited_for(component_id, lineage=lineage)
        elif nearest.palette.inheritance.override_policy is PaletteOverridePolicy.REJECT_CONFLICT:
            return PaletteResolution(component_id, None, None, None, "rejected", "local palette conflicts with nearest ancestor REJECT_CONFLICT policy", fingerprint)
        else:
            raise PaletteError("unsupported palette override policy")
    elif nearest is not None:
        if not nearest.palette.inheritance.allow_children:
            return PaletteResolution(component_id, None, None, None, "unresolved", "nearest palette authority blocks inheritance", fingerprint)
        hierarchy = list(reversed(_ancestors_nearest_first(graph, component_id)))
        start = next(i for i, item in enumerate(hierarchy) if item.id == nearest.id)
        lineage = tuple(item.id for item in hierarchy[start:] + [component])
        authority = nearest.palette.inherited_for(component_id, lineage=lineage)
    else:
        return PaletteResolution(component_id, None, None, None, "unresolved", "no local or inherited palette authority", fingerprint)

    if slot is None:
        return PaletteResolution(component_id, authority, None, None, "resolved", "palette authority resolved; no slot requested", fingerprint)
    entry = authority.get(slot)
    if entry is None:
        return PaletteResolution(component_id, None, None, None, "unresolved", f"palette slot '{slot.value}' is absent", fingerprint)
    return PaletteResolution(component_id, authority, slot, entry, "resolved", "palette slot selected deterministically", fingerprint)


def palette_invalidation(graph: RuntimeGraph, target_component_id: str, changed_component_id: str) -> tuple[bool, str]:
    """Report whether a palette mutation can affect a target composition."""
    if target_component_id not in graph.nodes or changed_component_id not in graph.nodes:
        raise KeyError("palette invalidation references an unknown component")
    if target_component_id == changed_component_id:
        return True, "target palette authority changed"
    current = graph.get(target_component_id)
    while current.parent_id is not None:
        current = graph.get(current.parent_id)
        if current.id == changed_component_id:
            if graph.get(target_component_id).component.palette is not None:
                nearest = _nearest_palette(graph, target_component_id)
                if nearest is not None and nearest.palette.inheritance.override_policy is PaletteOverridePolicy.LOCAL_WINS:
                    return False, "local palette authority wins over ancestor"
            return True, "ancestor may change inherited palette resolution"
    return False, "changed component is outside the target palette authority chain"
