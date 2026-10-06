# Iris invariants and assumptions — V1.84

## Invariants

`INV-IRIS-001` — count fields are integer values and bool is not accepted.

`INV-IRIS-002` — `ring_count` is non-negative and `pattern_count` is strictly positive.

`INV-IRIS-003` — all four Real-valued local parameters are finite and non-bool.

`INV-IRIS-004` — glow, opacity and pattern strength remain within `[0,1]`; outline width remains non-negative.

`INV-IRIS-005` — authored colour values pass the shared validator.

`INV-IRIS-006` — `IrisSpec` remains immutable and valid authored values are not coerced or rewritten.

## Assumptions

- downstream renderer receives a validated `IrisSpec`;
- the existing renderer uses count fields as integer loop bounds;
- visual-only iris fields remain outside the geometry cache key by existing design;
- deeper iris morphology and optical relations remain owned elsewhere.

## Explicit non-guarantees

V1.84 does not certify a maximum ring/pattern count, iris morphology quality, gaze behaviour, pupil containment,
corneal optics, occlusion or artistic quality.
