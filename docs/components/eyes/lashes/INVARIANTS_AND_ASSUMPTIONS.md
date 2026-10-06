# CMP-EYE-LASH — invariants and assumptions

## INV-LASH-001

`enabled` is boolean.

## INV-LASH-002

Every numeric field used by the lash spec is finite and non-bool numeric.

## INV-LASH-003

`count` is integral and non-negative; renderer iteration therefore receives an integer-compatible authored value.

## INV-LASH-004

Bounded controls remain within their existing ranges. V1.85 does not introduce new ranges.

## INV-LASH-005

Existing valid authored defaults and style presets remain constructible.

## INV-LASH-006

Frozen dataclass semantics remain unchanged.

## Assumptions explicitly not promoted

- No maximum lash count is invented; resource ceilings remain outside this local contract.
- No new biological/anatomical lash morphology is inferred.
- No visual proportion is changed.
- No cache identity is changed because this brick changes validation only.
- No persistence contract is promoted without a verified adapter.
