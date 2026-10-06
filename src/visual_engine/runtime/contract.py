from __future__ import annotations

from dataclasses import replace
from typing import Mapping, cast

from visual_engine.components.common.meta import Component
from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.visual_contract import (
    ContourContract,
    LocalTransform,
    MaterialContract,
    MaterialOverride,
    ResolvedVisualContract,
    VisualContract,
)
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.provenance import ResolutionProvenance, ResolutionStep
from visual_engine.runtime.versioning import ResolutionFingerprint, VersionStamp, resolution_fingerprint
from visual_engine.runtime.resolution_cache import ResolutionCache
from visual_engine.runtime.state_policy import collect_state_activations, resolve_state_activations_with_decisions
from visual_engine.runtime.effects import (
    resolve_effects,
    EFFECT_COLOR_CALCULATION_SPACE,
    EFFECT_COLOR_OPERATION_ID,
    EFFECT_COLOR_OPERATION_VERSION,
)
from visual_engine.runtime.resolution_context import ResolutionContext
from visual_engine.runtime.resolved_component import ResolutionTrace, ResolvedComponent
from visual_engine.runtime.dependencies import relation_effects


def _matmul(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(3)) for j in range(3)) for i in range(3))



def _resolve_contour(parent: ContourContract, local: ContourContract | None, override) -> ContourContract:
    if override is None:
        return local if local is not None else parent
    return ContourContract(
        color=override.color if override.color is not None else parent.color,
        width=override.width if override.width is not None else parent.width,
        opacity=override.opacity if override.opacity is not None else parent.opacity,
        style=override.style if override.style is not None else parent.style,
        cap=override.cap if override.cap is not None else parent.cap,
        join=override.join if override.join is not None else parent.join,
    )


def _resolve_material(parent: MaterialContract, local: MaterialContract | None, override: MaterialOverride | None) -> MaterialContract:
    base = local if local is not None else parent
    if override is None:
        return base
    return MaterialContract(
        name=override.name if override.name is not None else parent.name,
        roughness=override.roughness if override.roughness is not None else parent.roughness,
        metallic=override.metallic if override.metallic is not None else parent.metallic,
        transmission=override.transmission if override.transmission is not None else parent.transmission,
        emission=override.emission if override.emission is not None else parent.emission,
    )


def _merge_states(context_states: tuple[str, ...], components: list[Component]) -> tuple[str, ...]:
    names = set(context_states)
    for component in components:
        names.update(layer.name for layer in component.state if layer.enabled)
    return tuple(sorted(names))


def resolve_component(
    graph: RuntimeGraph,
    component_id: str,
    *,
    context: ResolutionContext | None = None,
    version: VersionStamp | None = None,
    cache: ResolutionCache | None = None,
) -> ResolvedComponent:
    """Resolve a component, optionally reusing an exact immutable cache entry.

    When a cache is supplied, the current graph is checked before fingerprint
    construction and ``ResolutionCache.get_or_build`` owns same-key MISS
    coalescing. The uncached resolver remains the sole authority for resolution.
    """
    context = context or ResolutionContext()
    version = version or VersionStamp()
    if cache is None:
        return _resolve_component_uncached(
            graph, component_id, context=context, version=version,
        )

    # A stale topology must never become a cache lookup surface. Local visual
    # mutations remain fingerprint-owned; RuntimeGraph owns topology freshness.
    if not graph.is_current():
        raise RuntimeError(
            "RuntimeGraph is stale: component hierarchy or relation topology changed; "
            "rebuild the graph before using ResolutionCache"
        )

    requested_fingerprint = resolution_fingerprint(graph, component_id, context, version)

    # The cache now coalesces concurrent same-key MISSes. Only its first caller
    # builds; waiters receive the exact same immutable ResolvedComponent object.
    result, _reused = cache.get_or_build(
        requested_fingerprint,
        lambda: _resolve_component_uncached(
            graph, component_id, context=context, version=version,
            fingerprint=requested_fingerprint,
        ),
    )
    return cast(ResolvedComponent, result)


def _resolve_component_uncached(
    graph: RuntimeGraph,
    component_id: str,
    *,
    context: ResolutionContext,
    version: VersionStamp,
    fingerprint: ResolutionFingerprint | None = None,
) -> ResolvedComponent:
    """Perform the authoritative resolution without cache policy.

    Cache lifetime, stale-graph checks and same-key concurrency belong to the
    outer wrapper. Keeping this computation cache-free makes it impossible for
    the resolver to accidentally publish a partial result or a second cache law.
    """
    node = graph.get(component_id)
    chain: list[Component] = []
    current = node
    while True:
        chain.append(current.component)
        if current.parent_id is None:
            break
        current = graph.get(current.parent_id)
    chain.reverse()

    world = ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    world_z = 0.0
    resolved = VisualContract()
    trace: list[str] = []
    provenance: list[ResolutionStep] = []

    for index, component in enumerate(chain):
        world = _matmul(world, component.transform.matrix())
        world_z += component.transform.z
        if index == 0:
            resolved = component.visual
            trace.append(f"{component.id}.visual=explicit-root")
            provenance.extend([
                ResolutionStep("fill_color", component.id, "set", "explicit-root"),
                ResolutionStep("contour", component.id, "set", "explicit-root"),
                ResolutionStep("material", component.id, "set", "explicit-root"),
                ResolutionStep("opacity", component.id, "set", "explicit-root"),
                ResolutionStep("visibility", component.id, "set", "explicit-root"),
            ])
            continue

        override = component.visual_overrides
        if override is None:
            # Backwards-compatible explicit local contract.
            resolved = VisualContract(
                fill_color=component.visual.fill_color,
                contour=component.visual.contour,
                material=component.visual.material,
                opacity=resolved.opacity * component.visual.opacity,
                visibility=resolved.visibility * component.visual.visibility,
            )
            trace.append(f"{component.id}.visual=explicit-legacy")
            provenance.extend([
                ResolutionStep("fill_color", component.id, "replace", "legacy-explicit", "descendant local VisualContract"),
                ResolutionStep("contour", component.id, "replace", "legacy-explicit", "descendant local VisualContract"),
                ResolutionStep("material", component.id, "replace", "legacy-explicit", "descendant local VisualContract"),
                ResolutionStep("opacity", component.id, "multiply", "hierarchical", "parent × local"),
                ResolutionStep("visibility", component.id, "multiply", "hierarchical", "parent × local"),
            ])
        else:
            resolved = VisualContract(
                fill_color=override.fill_color if override.fill_color is not None else resolved.fill_color,
                contour=_resolve_contour(resolved.contour, None, override.contour),
                material=_resolve_material(resolved.material, None, override.material),
                opacity=resolved.opacity * (override.opacity if override.opacity is not None else 1.0),
                visibility=resolved.visibility * (override.visibility if override.visibility is not None else 1.0),
            )
            trace.append(f"{component.id}.visual_overrides=inherit-or-override")
            provenance.extend([
                ResolutionStep("fill_color", component.id, "inherit" if override.fill_color is None else "override", "field-level", "None=inherit"),
                ResolutionStep("contour", component.id, "inherit" if override.contour is None else "override", "field-level", "field-level contour merge"),
                ResolutionStep("material", component.id, "inherit" if override.material is None else "override", "field-level", "field-level material merge"),
                ResolutionStep("opacity", component.id, "inherit" if override.opacity is None else "multiply", "hierarchical", "None=identity; numeric=parent × local"),
                ResolutionStep("visibility", component.id, "inherit" if override.visibility is None else "multiply", "hierarchical", "None=identity; numeric=parent × local"),
            ])

    state_groups = dict(context.state_groups)
    state_conflicts = dict(context.state_conflicts)
    state_requires = dict(context.state_requires)
    state_candidates = collect_state_activations(
        tuple(chain), context.active_states,
        context_priority=context.state_priority,
        context_groups=state_groups,
        context_conflicts=state_conflicts,
        context_requires=state_requires,
    )
    # Consequence-derived activations join the existing policy as candidates.
    # The state policy remains the single owner of precedence, exclusivity,
    # conflicts, and requirements.
    state_resolved, state_decisions = resolve_state_activations_with_decisions(
        tuple(state_candidates) + tuple(context.consequence_states)
    )
    states = tuple(item.name for item in state_resolved)
    for decision in state_decisions:
        item = decision.candidate
        provenance.append(ResolutionStep(
            "states", item.source_id, decision.action, "precedence",
            f"state={item.name};priority={item.priority};group={item.group};specificity={item.specificity};reason={decision.reason}",
        ))
    effects = tuple(sorted(
        context.effective_effects(component_id) + relation_effects(graph, component_id),
        key=lambda effect: effect.precedence_key,
    ))
    fill, contour_color, effect_opacity, effect_visibility, shadow_alpha, ordered_effects = resolve_effects(
        effects,
        base_fill=resolved.fill_color,
        base_contour=resolved.contour.color,
        base_opacity=max(0.0, min(1.0, resolved.opacity)),
        base_visibility=max(0.0, min(1.0, resolved.visibility)),
    )
    contour = replace(resolved.contour, color=contour_color)
    for effect in ordered_effects:
        policy = "effect-precedence"
        detail = f"effect={effect.effect_id};priority={effect.priority};target={effect.target_id or '*'}"
        if effect.kind in {"shadow", "tint"}:
            # The first real downstream color operation is explicitly named in
            # provenance. Its calculation space is sRGB8 for visual continuity,
            # while its input/output representation remains canonical ColorRGBA.
            policy = EFFECT_COLOR_OPERATION_ID
            detail += (
                f";operation_version={EFFECT_COLOR_OPERATION_VERSION}"
                f";calculation_space={EFFECT_COLOR_CALCULATION_SPACE}"
                ";alpha_mode=base_preserved/effect_alpha_controls_rgb"
            )
        provenance.append(ResolutionStep(
            effect.kind, effect.source_id, "apply", policy, detail,
        ))
    resolved_visual = ResolvedVisualContract(
        world_transform=world,
        world_z=world_z + node.component.geometry.local_z,
        visibility=effect_visibility,
        opacity=effect_opacity,
        effective_fill_color=fill,
        effective_contour=contour,
        material=resolved.material,
        shadow_alpha=shadow_alpha,
        shadow_color=(ordered_effects[-1].color if ordered_effects and ordered_effects[-1].kind in {"shadow", "tint"} else context.shadow_color).lower(),
        occluded_by=tuple(context.occluded_by),
        active_states=states,
        applied_effect_ids=tuple(effect.effect_id for effect in ordered_effects),
    )
    provenance.extend([
        ResolutionStep("states", node.component.id, "resolve", "precedence", "priority + source rank + specificity + conflicts + requirements"),
        ResolutionStep("effects", node.component.id, "resolve", "precedence", "priority-ordered effects with typed composition laws"),
        ResolutionStep("world_transform", node.component.id, "compose", "matrix", "root→target ordered multiplication"),
        ResolutionStep("world_z", node.component.id, "accumulate", "additive", "ancestor z + target geometry.local_z"),
    ])
    result = ResolvedComponent(
        component_id=node.component.id,
        kind=node.component.kind,
        visual=resolved_visual,
        geometry=node.component.geometry,
        trace=ResolutionTrace(tuple(trace)),
        provenance=ResolutionProvenance(tuple(provenance)),
        version=version,
        fingerprint=fingerprint or resolution_fingerprint(graph, component_id, context, version),
    )
    return result


def resolve_component_contract(
    graph: RuntimeGraph,
    component_id: str,
    *,
    shadow_alpha: float = 0.0,
    shadow_color: str = "#000000",
    occluded_by: tuple[str, ...] = (),
    active_states: tuple[str, ...] = (),
    version: VersionStamp | None = None,
    cache: ResolutionCache | None = None,
) -> ResolvedVisualContract:
    """Compatibility wrapper returning only the historical visual contract."""
    return resolve_component(
        graph,
        component_id,
        context=ResolutionContext(
            shadow_alpha=shadow_alpha,
            shadow_color=shadow_color,
            occluded_by=occluded_by,
            active_states=active_states,
        ),
        version=version,
        cache=cache,
    ).visual
