# Pre-change impact audit — V1.72

`CMP-RUNTIME-STATE-POLICY-CONTRACT`.

## VERIFY

Starting checkpoint: certified V1.71. The checkpoint archive and SHA-256 were verified. Status, roadmap, architecture principles/tree, V1.71 contract, decisions, component truth and artifact policy were read. The fresh workspace was checked with the architectural preflight.

## ARCHITECT

Fresh source audit rejected the previously known `resolve_component_contract` seam again as a compatibility-cycle risk. A separate existing responsibility was found in `runtime.state_policy`: the immutable `StateActivation`/`StateDecision` value contracts are consumed independently by `resolution_context`, `consequence_bindings` and the public runtime boundary, while precedence algorithms remain local to `state_policy`.

Owner: `src/visual_engine/runtime/state_policy_contract.py:1-37`.
Parent: `runtime.state_policy`.
Children: none.
Non-responsibility: all state-resolution algorithms and every downstream appearance/geometry/render concern.

## IMPACT

- Files: new contract owner; compatibility resolver facade; direct production consumers; public export; dedicated tests; truth dossier; governance records.
- Consumers: traced direct imports only; no inferred consumer.
- Parent/siblings: `state_policy` remains resolver owner; `resolution_context` and `consequence_bindings` remain consumers.
- Contracts/invariants: frozen/slotted classes and precedence tuple preserved exactly.
- Cache/fingerprint/provenance: no algorithm or identity change.
- Persistence/database: no consumer or migration impact.
- Determinism: state outputs and production five-case identities must remain equal to V1.71.
- Visual: state resolution is upstream of production rendering, so real five-case QA is mandatory.

## Reopen conditions

Any new cycle, duplicate owner, public identity drift, state-decision drift, persistence consumer, cache/fingerprint change, or production visual/result identity change reopens IMPACT before certification.
