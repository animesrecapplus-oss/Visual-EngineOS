# V1.84 decisions

`DEC-018-001` — Iris is selected only after a fresh horizontal audit proves an executable owner, real consumers,
local responsibility and a concrete validation defect.

`DEC-018-002` — the V1.84 runtime scope is exactly `IrisSpec` local numeric/type validation; no geometry or morphology
expansion is permitted.

`DEC-018-003` — count fields use `Integral`; real-valued fields use `Real` plus explicit bool rejection and
`math.isfinite`; strings are not coerced.

`DEC-018-004` — no arbitrary maximum ring/pattern count is introduced without evidence or a measured resource contract.

`DEC-018-005` — valid authored values, shared colour validation, cache identity, renderer behaviour, COLOR and database
state remain unchanged.
