# Component truth

`CMP-RUNTIME-RESOLUTION-CONTEXT`.

## Identity

`FILE-RC-001`: canonical source `src/visual_engine/runtime/resolution_context.py:10-97`.
`TST-RC-001`: `tests/components/runtime/resolution_context/test_v168_resolution_context_truth.py:1-90`.

## Responsibility

Own the immutable `ResolutionContext` input contract: field validation, deterministic canonicalization, target-scoped effective-effect selection and legacy-shadow conversion.

## Non-responsibility

- state precedence/conflict resolution;
- visual-effect composition;
- resolution fingerprint calculation;
- resolution cache ownership;
- geometry/transform/rendering;
- COLOR algorithms;
- persistence/database.
