# CMP-EYE-LASH — pre-change impact audit V1.85

## Verified facts

- Owner: `src/visual_engine/components/face/eyes/lashes/spec.py`.
- Direct render consumers execute `range(lashes.count)` / `range(lower_lashes.count)`.
- Existing constructor accepts fractional/bool counts and selected non-finite real values.
- No direct database adapter or migration is verified for LashSpec.
- No cache/fingerprint algorithm directly owned by this spec module is verified.

## Authorized change

Only local constructor validation in `LashSpec` and `LowerLashSpec`.

## Protected behavior

Valid defaults, public field names, style/form vocabulary, colour validation, dataclass immutability, renderer
algorithms, terminal exclusion, visibility, cache behavior, persistence, API exports and deterministic output.

## Re-open trigger

If implementation reveals a consumer-specific contract, persistence dependency, cache dependency, or visual ownership
that is not covered here, stop, update this impact audit and re-evaluate before continuing.
