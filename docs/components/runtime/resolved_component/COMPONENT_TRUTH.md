# Component truth

`CMP-RUNTIME-RESOLVED-COMPONENT`.

## Identity

`FILE-RCMP-001`: `src/visual_engine/runtime/resolved_component.py:17-35`.
`TST-RCMP-001`: `tests/components/runtime/resolved_component/test_v169_resolved_component_truth.py:1-64`.

## Responsibility

Own the immutable renderer-neutral `ResolvedComponent` result envelope and its legacy `ResolutionTrace` value type.

## Non-responsibility

- resolution execution or policy;
- state/effect precedence;
- provenance generation;
- fingerprint calculation;
- cache ownership/policy;
- geometry generation/transform;
- rendering/visibility/occlusion;
- COLOR algorithms;
- persistence/database.
