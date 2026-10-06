# Decisions

`DEC-RC-001`: V1.68 selects `ResolutionContext` as the next seam because it is a distinct immutable input contract with four real production consumers, while `runtime.contract` mixes that contract with resolution/result responsibilities.

`DEC-RC-002`: extract only `ResolutionContext`; `ResolutionTrace`, `ResolvedComponent`, resolver helpers and resolver execution remain in `runtime.contract`.

`DEC-RC-003`: direct production consumers use the canonical owner; `consequence_bindings` retains its lazy facade import because no cycle-safe direct migration is required by this brick.

`DEC-RC-004`: `runtime.contract` remains the historical compatibility facade and imports the canonical object.

`DEC-RC-005`: no COLOR, database, persistence, cache-policy or fingerprint algorithm change is authorized.
