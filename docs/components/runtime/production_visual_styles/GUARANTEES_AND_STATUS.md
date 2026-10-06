# Guarantees and status

Guarantees:
- one canonical owner for the existing production geometry-owner style-map construction;
- root resolution is not duplicated;
- non-root appearance remains owned by `resolve_component` and its existing fingerprint/cache contract;
- unknown non-root owners retain the former ignore behavior;
- deterministic owner ordering is preserved;
- no geometry, occlusion, COLOR, database or cache-lifetime semantics are changed.

Status: `CERTIFIED V1.61` only after the full component gate, deterministic regression, dependency/cycle/duplicate audits,
visual identity evidence, documentation and artifact cleanup pass.
