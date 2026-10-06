# Iris decisions — V1.84

`DEC-EYE-IRIS-001` — select Iris after a fresh horizontal audit because it has a real executable owner, real
consumers, a bounded local responsibility and a reproduced validation defect.

`DEC-EYE-IRIS-002` — harden only the local IrisSpec numeric/type boundary; do not expand into geometry or morphology.

`DEC-EYE-IRIS-003` — use `numbers.Integral` for count fields and `numbers.Real` plus explicit bool rejection and
`math.isfinite` for real-valued fields; do not coerce strings.

`DEC-EYE-IRIS-004` — do not invent a maximum count without evidence from an existing contract or measured resource
requirement.

`DEC-EYE-IRIS-005` — preserve shared colour validation and all valid authored values.

`DEC-EYE-IRIS-006` — preserve cache identity, renderer semantics, COLOR boundary and database state.

`DEC-EYE-IRIS-007` — do not create or infer Git cleanliness from an archive. Certification remains BLOCKED until a real
repository checkout permits verification of repository state.
