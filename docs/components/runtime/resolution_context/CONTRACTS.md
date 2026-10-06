# Contracts

`CON-RC-001`: `ResolutionContext` is frozen and slot-based.

`CON-RC-002`: `shadow_alpha` is finite and in `[0,1]`; `shadow_color` is hexadecimal `#RRGGBB` or `#RRGGBBAA`.

`CON-RC-003`: active states and mapping keys are non-empty strings; state mappings are canonicalized and duplicate keys are rejected.

`CON-RC-004`: effects are `VisualEffect` instances with unique IDs and deterministic precedence ordering.

`CON-RC-005`: consequence states are `StateActivation` instances ordered by their existing precedence key; this contract does not resolve them.

`CON-RC-006`: `effective_effects(component_id)` keeps global/targeted effects and converts legacy shadow fields to one target-scoped effect.

`CON-RC-007`: `runtime.contract.ResolutionContext` and `runtime.ResolutionContext` remain identity-compatible re-exports of the canonical owner.
