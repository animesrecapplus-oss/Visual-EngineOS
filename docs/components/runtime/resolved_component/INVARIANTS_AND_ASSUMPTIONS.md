# Invariants and assumptions

`INV-RCMP-001`: result construction is value-preserving; the owner does not resolve or normalize inputs.

`INV-RCMP-002`: frozen/slot semantics prevent ordinary post-construction mutation or undeclared attributes.

`INV-RCMP-003`: `ResolutionTrace` remains deterministic data carried by the result; structured provenance remains
owned by `runtime.provenance`.

`INV-RCMP-004`: fingerprint identity remains owned by `runtime.versioning`; this owner never recomputes it.

`INV-RCMP-005`: extraction does not alter resolution output, cache identity, SVG output, visibility or geometry.

Assumption: existing `GeometryContract`, `ResolvedVisualContract`, `ResolutionProvenance`, `VersionStamp` and
`ResolutionFingerprint` remain the semantic owners of their fields.
