# CMP-EYE-LASH — errors

## ERR-LASH-001 — fractional/bool count accepted pre-V1.85

`LashSpec(count=2.5)` and `LashSpec(count=True)` were accepted even though the production renderer executes
`range(lashes.count)`. This was reproduced before modification.

## ERR-LASH-002 — non-finite real fields accepted pre-V1.85

Examples including `length=inf`, `thickness=nan`, `spacing_jitter=nan` and `curvature=nan` were accepted because the
previous checks only used relational comparisons.

## ERR-LASH-003 — coercive enabled values

String/integer values for `enabled` were accepted pre-V1.85 even though the field is boolean.

## ERR-LASH-004 — no evidence of a resource ceiling

A maximum count is not currently verified. This remains an explicit unresolved boundary rather than an invented rule.

## V1.85 resolution

ERR-LASH-001 through ERR-LASH-003 are resolved by strict local numeric/type validation. ERR-LASH-003 remains outside
scope.
