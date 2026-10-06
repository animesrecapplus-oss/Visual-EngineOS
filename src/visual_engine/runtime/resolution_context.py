from __future__ import annotations

from dataclasses import dataclass
import math

from visual_engine.runtime.effects import VisualEffect
from visual_engine.runtime.state_policy import StateActivation


@dataclass(frozen=True, slots=True)
class ResolutionContext:
    """Immutable external input contract for generic component resolution.

    This module owns context validation/canonicalization only. State/effect
    semantics remain in their dedicated policies; fingerprinting remains in
    ``versioning`` and consumes this contract without owning it.
    """

    shadow_alpha: float = 0.0
    shadow_color: str = "#000000"
    occluded_by: tuple[str, ...] = ()
    active_states: tuple[str, ...] = ()
    state_priority: int = 1000
    state_groups: tuple[tuple[str, str], ...] = ()
    state_conflicts: tuple[tuple[str, tuple[str, ...]], ...] = ()
    state_requires: tuple[tuple[str, tuple[str, ...]], ...] = ()
    effects: tuple[VisualEffect, ...] = ()
    # Consequence-derived activations enter the existing state policy; this
    # field never creates a second precedence engine.
    consequence_states: tuple[StateActivation, ...] = ()

    def __post_init__(self) -> None:
        if not math.isfinite(self.shadow_alpha) or not 0 <= self.shadow_alpha <= 1:
            raise ValueError("shadow_alpha must be in [0,1]")
        if not isinstance(self.shadow_color, str) or len(self.shadow_color) not in (7, 9) or not self.shadow_color.startswith("#"):
            raise ValueError("shadow_color must be #RRGGBB or #RRGGBBAA")
        try:
            int(self.shadow_color[1:], 16)
        except ValueError as exc:
            raise ValueError("shadow_color must be hexadecimal") from exc
        if any(not isinstance(v, str) or not v for v in self.occluded_by):
            raise ValueError("occluded_by entries must be non-empty strings")
        states = tuple(sorted(set(self.active_states)))
        if any(not isinstance(v, str) or not v for v in states):
            raise ValueError("active_states entries must be non-empty strings")
        object.__setattr__(self, "active_states", states)
        if not isinstance(self.state_priority, int):
            raise ValueError("state_priority must be an integer")
        for field_name, mapping in (
            ("state_groups", self.state_groups),
            ("state_conflicts", self.state_conflicts),
            ("state_requires", self.state_requires),
        ):
            keys = [item[0] for item in mapping]
            if any(not isinstance(k, str) or not k for k in keys) or len(set(keys)) != len(keys):
                raise ValueError(f"{field_name} keys must be unique non-empty strings")
        groups = dict(self.state_groups)
        if any(not isinstance(k, str) or not k or not isinstance(v, str) or not v for k, v in groups.items()):
            raise ValueError("state_groups entries must be non-empty strings")
        conflicts = {k: tuple(sorted(set(v))) for k, v in self.state_conflicts}
        requires = {k: tuple(sorted(set(v))) for k, v in self.state_requires}
        if any(not k or any(not x for x in v) for k, v in (*conflicts.items(), *requires.items())):
            raise ValueError("state conflict/requirement names must be non-empty")
        object.__setattr__(self, "state_groups", tuple(sorted(groups.items())))
        object.__setattr__(self, "state_conflicts", tuple(sorted(conflicts.items())))
        object.__setattr__(self, "state_requires", tuple(sorted(requires.items())))
        if any(not isinstance(v, VisualEffect) for v in self.effects):
            raise ValueError("effects must contain VisualEffect instances")
        if any(not isinstance(v, StateActivation) for v in self.consequence_states):
            raise ValueError("consequence_states must contain StateActivation instances")
        object.__setattr__(
            self,
            "consequence_states",
            tuple(sorted(self.consequence_states, key=lambda s: s.precedence_key, reverse=True)),
        )
        effect_ids = [effect.effect_id for effect in self.effects]
        if len(effect_ids) != len(set(effect_ids)):
            raise ValueError("effect IDs must be unique within a resolution context")
        object.__setattr__(self, "effects", tuple(sorted(self.effects, key=lambda e: e.precedence_key)))

    def effective_effects(self, component_id: str) -> tuple[VisualEffect, ...]:
        """Return target-applicable effects, preserving the legacy shadow boundary."""
        effects = list(self.effects)
        if self.shadow_alpha:
            effects.append(
                VisualEffect(
                    effect_id="__legacy_shadow__",
                    kind="shadow",
                    priority=-1,
                    alpha=self.shadow_alpha,
                    color=self.shadow_color,
                    source_id=component_id,
                    target_id=component_id,
                    metadata=(("origin", "legacy_shadow"),),
                )
            )
        return tuple(effect for effect in effects if effect.target_id is None or effect.target_id == component_id)
