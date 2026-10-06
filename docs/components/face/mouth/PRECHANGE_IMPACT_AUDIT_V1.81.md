# V1.81 pre-change impact audit — CMP-FACE-MOUTH

## Selection

`CMP-FACE-MOUTH` is selected as the different mature micro-component after V1.80 Ear.
It has a real executable owner, real production consumers, an existing truth dossier,
a cache path, persistence coverage, visibility relations and focused tests.

## Observed boundary defect before modification

The generic `Parameter` constructor rejects malformed values, but a malformed `Component`
can still carry a manually constructed/bypassed `Parameter`. The current mouth `_value()`
uses `float(parameter.value)`, which accepts `bool` and numeric strings. A positive subnormal
width can also become a zero radius after multiplication by `0.5`.

Reproduction from the V1.80 checkpoint:

- `True` width: accepted as `1.0`.
- string `"0.2"` width: accepted as `0.2`.
- positive subnormal `5e-324`: accepted and produces `rx=0.0`.
- NaN/∞ eventually fail inside generic geometry bounds, but only after partial geometry construction.

## Authorized scope

Only the malformed width/height input boundary of `src/visual_engine/components/face/mouth.py`
and its focused adversarial tests may change. Valid production geometry, generator identity,
composite ownership, visibility, cache policy, persistence, COLOR and renderer semantics remain unchanged.

## Impact checklist

- Files: `mouth.py`, focused mouth hostile tests, mouth truth dossier, V1.81 governance/evidence files.
- Consumers: HumanFace → mouth composite → production render/visibility; registry unchanged.
- Parent/siblings: HumanFace, Eye, Nose, Ear, Hair unchanged.
- Contract: strengthen the existing finite-positive width/height contract to cover bypassed state.
- Invariants: finite positive dimensions and positive representable radii become leaf-owned guards.
- Tests: focused malformed-input tests plus mouth production, persistence, visibility and full regression.
- Cache/fingerprint/provenance: invalid inputs fail before cacheable geometry; valid cache identity is unchanged.
- Persistence/database: generic payload only; no schema or migration change.
- Determinism: no randomness or ordering change.
- Visual: valid production output must remain identical; no new visual-quality claim is permitted.
- Preserved behavior: all valid finite positive dimensions and existing composite/visibility behavior.
