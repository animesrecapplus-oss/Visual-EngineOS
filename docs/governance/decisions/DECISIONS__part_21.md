# Decisions — V1.87

## DEC-V187-001 — select Eyebrow horizontally

A fresh audit selected `CMP-EYE-EYEBROW` because it has a verified executable owner, real consumers and a reproducible
local validation defect. V1.84/V1.85/V1.86 recent hardening owners are deferred; planned anatomy without an executable
owner is not promoted.

## DEC-V187-002 — keep validation local

Only `eyebrow/spec.py` changes at runtime. The shared `_finite` helper is not modified because doing so would widen the
impact surface to unrelated components.

## DEC-V187-003 — reject unsafe numeric representation

A huge integer can raise `OverflowError` when passed to `math.isfinite`. The local contract therefore rejects values
that cannot be safely evaluated as finite instead of leaking that implementation exception.

## DEC-V187-004 — preserve placement authority

Existing eye-gap ranges remain the only local numeric authority. No new anatomical proportion, resource ceiling or
placement algorithm is introduced.
