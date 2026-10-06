# CMP-EYE-LASH — test status

## Baseline

V1.84 full regression: 1221 PASS, 1 expected PostgreSQL SKIP, 0 FAIL.

## V1.85 focused scope

The focused suite will cover both `LashSpec` and `LowerLashSpec`, including NaN, +/-inf, bool/fractional counts, coercive numeric strings, coercive enabled values, negative/boundary
values, invalid vocabulary and valid authored defaults.

## Certification rule

Focused PASS is necessary but insufficient. Full regression, compile, dependency/cycle/duplicate, deterministic
render comparison, artifact hygiene and evidence verification are required before certification.
