# CMP-EYE-LASH — contracts

## CON-LASH-001 — enabled type

`enabled` must be a real boolean; coercive strings and integers are rejected.

## CON-LASH-002 — finite real numeric fields

All lash morphology/opacity real-valued fields must be `numbers.Real`, must not be `bool`, and must be finite.

## CON-LASH-003 — count type

`count` must be an integral value, must not be `bool`, and must be non-negative. Fractional numeric counts are
invalid because the production renderer iterates the count.

## CON-LASH-004 — bounded upper-lash fields

`density`, `outer_flare`, `inner_length_factor`, `upward_bias` and `taper` remain in `[0,1]`. `length`, `thickness`,
`curvature` and `spacing_jitter` remain non-negative.

## CON-LASH-005 — bounded lower-lash fields

`density`, `opacity`, `outer_flare`, `downward_bias` and `taper` remain in `[0,1]`. `length`, `thickness` and
`curvature` remain non-negative.

## CON-LASH-006 — existing vocabulary/colour

Existing style/form membership and shared hex colour validation remain unchanged.

## CON-LASH-007 — immutable compatibility

Both dataclasses remain frozen/slot-based and retain their existing public fields/defaults.

## INV-LASH-001

No NaN or infinity can enter a LashSpec numeric field.

## INV-LASH-002

No bool or fractional count can enter the lash renderer path through these specifications.
