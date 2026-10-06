# Decisions

`DEC-RCMP-001`: select the immutable result-envelope responsibility only after the fresh V1.68 consumer audit.

`DEC-RCMP-002`: move `ResolutionTrace` with `ResolvedComponent` because it is a value field of the same immutable
result contract; no second production responsibility is introduced.

`DEC-RCMP-003`: keep resolver execution in `runtime.contract`; no resolver rewrite is authorized.

`DEC-RCMP-004`: preserve compatibility identity through `runtime.contract` and the public `runtime` surface.

`DEC-RCMP-005`: freeze COLOR, database, persistence, cache policy and fingerprint algorithms for V1.69.
