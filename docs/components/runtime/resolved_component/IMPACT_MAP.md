# Impact map

`IMP-RCMP-001`: source owner — create `resolved_component.py`, remove result definitions from `contract.py`.

`IMP-RCMP-002`: consumers — production output annotation and resolver construction move to canonical owner.

`IMP-RCMP-003`: public API — compatibility imports remain identity-compatible.

`IMP-RCMP-004`: cache/fingerprint — no algorithm or ownership change; object type remains immutable.

`IMP-RCMP-005`: provenance/version — typed fields remain supplied by their existing owners.

`IMP-RCMP-006`: persistence/database — no direct consumer; no schema change.

`IMP-RCMP-007`: COLOR/appearance — no semantic implementation change.

`IMP-RCMP-008`: rendering/visibility — production output must remain identical.

`IMP-RCMP-009`: dependency graph — one new module and canonical edges; no new SCC permitted.

`IMP-RCMP-010`: artifacts/docs — V1.68 generated evidence is superseded; only V1.69 current evidence is retained.
