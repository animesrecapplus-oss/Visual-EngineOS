# Impact map — CMP-FACE-MOUTH — V1.81

## Pre-change finding

`CMP-FACE-MOUTH` was selected after V1.80 Ear by fresh owner/consumer/contract audit. The existing leaf contract said
finite positive dimensions, but `_value()` coerced arbitrary values with `float()`. A bypassed `Parameter` therefore
accepted bool/string values; positive subnormal width `5e-324` became `rx=0.0`. NaN/∞ reached generic geometry checks
only after partial construction.

## Authorized change

- `src/visual_engine/components/face/mouth.py:15-27,34-45` — strict numeric/non-boolean/finite validation and
  representable-radius guard.
- `tests/components/face/mouth/test_v181_mouth_input_hardening.py:1-45` — hostile boundary proof.

## Impact

- Consumers: production Mouth composite/render/visibility remain unchanged.
- Parent/siblings: HumanFace, Eye, Nose, Ear and Hair are unchanged.
- Contracts/invariants: existing finite-positive rule is made executable at the leaf even for bypassed state.
- Cache/fingerprint/provenance: invalid state fails before geometry exists; valid fingerprints are unchanged.
- Persistence/database: no schema, migration or serializer change.
- Determinism: no randomness, ordering or seed change.
- COLOR: no consumer or semantic change.
- Visual: valid front/±12° and visibility outputs are byte-identical to V1.80.
- Preserved behavior: every valid finite positive dimension retains the V1.80 geometry.
