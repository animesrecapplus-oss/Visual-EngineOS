from __future__ import annotations

"""V1.25 BASE authority resolution and appearance-only invalidation.

This module owns hierarchy semantics for the typed ``Component.base_color``
field.  Geometry is deliberately absent from every fingerprint here.  A local
BASE authority may override an inherited authority only according to the
nearest ancestor's explicit override policy; otherwise resolution fails closed.
"""

from dataclasses import dataclass
from visual_engine.components.common.base_color import (
    BaseColor,
    BaseColorError,
    BaseColorOverridePolicy,
    BaseColorInheritance,
    BaseColorRole,
)
from visual_engine.components.common.meta import Component
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.identity import stable_digest


BASE_COLOR_RESOLUTION_VERSION = "1"


@dataclass(frozen=True, slots=True)
class BaseColorResolution:
    target_component_id: str
    color: BaseColor | None
    status: str
    reason: str = ""
    dependency_fingerprint: str = ""

    def __post_init__(self) -> None:
        if not self.target_component_id:
            raise ValueError("BASE target component id is required")
        if self.status not in {"resolved", "unresolved", "rejected"}:
            raise ValueError("unsupported BASE resolution status")
        if self.status == "resolved" and self.color is None:
            raise ValueError("resolved BASE result requires a color")
        if self.status != "resolved" and self.color is not None:
            raise ValueError("non-resolved BASE result cannot carry a color")
        if self.status != "resolved" and not self.reason:
            raise ValueError("non-resolved BASE result requires a reason")
        if not self.dependency_fingerprint or len(self.dependency_fingerprint) != 64:
            raise ValueError("BASE dependency fingerprint must be SHA-256")


@dataclass(frozen=True, slots=True)
class BaseColorInvalidation:
    target_component_id: str
    changed_component_id: str
    affects_target: bool
    reason: str


def _ancestors_nearest_first(graph: RuntimeGraph, component_id: str) -> tuple[Component, ...]:
    current = graph.get(component_id)
    ancestors: list[Component] = []
    while current.parent_id is not None:
        current = graph.get(current.parent_id)
        ancestors.append(current.component)
    return tuple(ancestors)


def _authority_candidates(graph: RuntimeGraph, component_id: str) -> tuple[Component, ...]:
    """Return ancestors that could supply BASE, nearest first.

    A nearest ancestor carrying a BASE authority is the only authority consulted
    for inheritance.  Its ``allow_children`` policy can stop propagation; the
    resolver never skips over a blocking authority to invent a more distant one.
    """
    return tuple(component for component in _ancestors_nearest_first(graph, component_id) if component.base_color is not None)


def _validate_legacy_contradiction(component: Component) -> None:
    legacy = [layer for layer in component.appearance if "base_color" in layer.values]
    if component.base_color is not None and legacy:
        raise BaseColorError(
            f"component {component.id!r} has both typed BASE authority and legacy appearance base_color"
        )
    if len(legacy) > 1:
        raise BaseColorError(
            f"component {component.id!r} has multiple legacy BASE authorities"
        )


def adapt_legacy_base_color(
    component: Component,
    *,
    role: BaseColorRole | None = None,
    inheritance: BaseColorInheritance | None = None,
) -> BaseColor | None:
    """Explicitly adapt one legacy BASE layer to the typed contract.

    This is a migration adapter, not an automatic fallback.  It refuses multiple
    legacy authorities and refuses a simultaneous typed authority so a caller must
    make the source decision explicitly.
    """
    _validate_legacy_contradiction(component)
    if component.base_color is not None:
        raise BaseColorError("typed BASE authority already exists; legacy adapter is ambiguous")
    legacy = [layer for layer in component.appearance if "base_color" in layer.values]
    if not legacy:
        return None
    value = legacy[0].values["base_color"]
    if not isinstance(value, str):
        raise BaseColorError("legacy base_color must be an sRGB hexadecimal string")
    role = role or BaseColorRole.PRIMARY
    inheritance = inheritance or BaseColorInheritance()
    return BaseColor.from_srgb(component.id, value, source_id=f"legacy:{component.id}:{legacy[0].name}", role=role, inheritance=inheritance)


def _base_dependency_payload(graph: RuntimeGraph, component_id: str) -> dict:
    node = graph.get(component_id)
    local = node.component.base_color
    chain = [{"id": component_id, "base_color": local}]
    nearest = next((item for item in _authority_candidates(graph, component_id)), None)

    # Targeted invalidation: a LOCAL_WINS authority is self-contained, so an
    # ancestor color cannot invalidate it.  Other policies, and a blocking
    # ancestor, remain part of the dependency identity because they can change
    # the resolution status or inherited value.
    if local is None:
        if nearest is not None:
            chain.append({"id": nearest.id, "base_color": nearest.base_color})
    elif nearest is not None:
        policy = nearest.base_color.inheritance.override_policy
        if policy is not BaseColorOverridePolicy.LOCAL_WINS and nearest.base_color.inheritance.allow_children:
            chain.append({"id": nearest.id, "base_color": nearest.base_color})

    return {
        "contract_version": BASE_COLOR_RESOLUTION_VERSION,
        "target": component_id,
        "hierarchy": chain,
    }


def base_color_resolution_fingerprint(graph: RuntimeGraph, component_id: str) -> str:
    """Fingerprint only typed BASE inputs relevant to this target.

    Geometry, transforms, contours, materials, lighting, and unrelated siblings
    are absent by construction.  This is the targeted appearance invalidation key.
    """
    return stable_digest(_base_dependency_payload(graph, component_id))


def resolve_base_color(graph: RuntimeGraph, component_id: str) -> BaseColorResolution:
    """Resolve one component's typed BASE authority under explicit inheritance rules."""
    component = graph.get(component_id).component
    _validate_legacy_contradiction(component)
    for ancestor in _ancestors_nearest_first(graph, component_id):
        _validate_legacy_contradiction(ancestor)

    dependency_fingerprint = base_color_resolution_fingerprint(graph, component_id)
    local = component.base_color
    nearest = next((item for item in _authority_candidates(graph, component_id)), None)

    if local is not None:
        if nearest is None:
            return BaseColorResolution(component_id, local, "resolved", dependency_fingerprint=dependency_fingerprint)
        policy = nearest.base_color.inheritance.override_policy
        if policy is BaseColorOverridePolicy.LOCAL_WINS:
            return BaseColorResolution(component_id, local, "resolved", dependency_fingerprint=dependency_fingerprint)
        if policy is BaseColorOverridePolicy.INHERIT_WINS:
            if not nearest.base_color.inheritance.allow_children:
                return BaseColorResolution(component_id, local, "resolved", dependency_fingerprint=dependency_fingerprint)
            hierarchy = list(reversed(_ancestors_nearest_first(graph, component_id)))
            start = next(index for index, item in enumerate(hierarchy) if item.id == nearest.id)
            lineage = tuple(item.id for item in hierarchy[start:] + [component])
            inherited = nearest.base_color.inherited_for(component_id, lineage=lineage)
            return BaseColorResolution(
                component_id,
                inherited,
                "resolved",
                reason="nearest ancestor INHERIT_WINS",
                dependency_fingerprint=dependency_fingerprint,
            )
        if policy is BaseColorOverridePolicy.REJECT_CONFLICT:
            return BaseColorResolution(
                component_id,
                None,
                "rejected",
                "local BASE conflicts with nearest ancestor REJECT_CONFLICT policy",
                dependency_fingerprint,
            )
        raise BaseColorError(f"unsupported BASE override policy: {policy}")

    if nearest is None:
        return BaseColorResolution(
            component_id,
            None,
            "unresolved",
            "no local or inherited BASE authority",
            dependency_fingerprint,
        )
    if not nearest.base_color.inheritance.allow_children:
        return BaseColorResolution(
            component_id,
            None,
            "unresolved",
            "nearest BASE authority blocks inheritance",
            dependency_fingerprint,
        )

    hierarchy = list(reversed(_ancestors_nearest_first(graph, component_id)))
    try:
        start = next(index for index, item in enumerate(hierarchy) if item.id == nearest.id)
    except StopIteration as exc:  # pragma: no cover - nearest is derived from the same hierarchy
        raise BaseColorError("BASE authority disappeared during resolution") from exc
    lineage = tuple(item.id for item in hierarchy[start:] + [component])
    inherited = nearest.base_color.inherited_for(component_id, lineage=lineage)
    return BaseColorResolution(
        component_id,
        inherited,
        "resolved",
        reason="nearest ancestor inherited",
        dependency_fingerprint=dependency_fingerprint,
    )


def base_color_invalidation(
    graph: RuntimeGraph,
    target_component_id: str,
    changed_component_id: str,
) -> BaseColorInvalidation:
    """Explain whether one component's BASE mutation can affect a target."""
    if target_component_id not in graph.nodes or changed_component_id not in graph.nodes:
        raise KeyError("BASE invalidation references an unknown component")
    if target_component_id == changed_component_id:
        return BaseColorInvalidation(target_component_id, changed_component_id, True, "target BASE authority changed")
    current = graph.get(target_component_id)
    while current.parent_id is not None:
        current = graph.get(current.parent_id)
        if current.id == changed_component_id:
            return BaseColorInvalidation(
                target_component_id,
                changed_component_id,
                True,
                "ancestor may change inherited BASE resolution",
            )
    return BaseColorInvalidation(
        target_component_id,
        changed_component_id,
        False,
        "changed component is outside the target BASE authority chain",
    )
