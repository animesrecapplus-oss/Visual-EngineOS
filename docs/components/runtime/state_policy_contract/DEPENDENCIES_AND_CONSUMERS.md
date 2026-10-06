# Dependencies and consumers

## Dependencies

The canonical contract module depends only on Python dataclasses. It does not import the resolver or runtime graph. Production consumers continue through the established compatibility facade; no public import path is broken.

## Real consumers

- `src/visual_engine/runtime/state_policy.py:8` — compatibility facade and resolver annotations/construction.
- `src/visual_engine/runtime/state_policy.py:8` — compatibility facade and resolver annotations/construction.
- `src/visual_engine/runtime/consequence_bindings.py:15` — consumes `StateActivation` through the compatibility surface.
- `src/visual_engine/runtime/resolution_context.py:7` — consumes `StateActivation` through the compatibility surface.
- `src/visual_engine/runtime/__init__.py:15,27` — public compatibility exports.
- `tests/components/runtime/resolution_context/test_v168_resolution_context_truth.py:12` — compatibility/type evidence.

## Persistence / database

No persistence or PostgreSQL consumer is present for these runtime value contracts. No migration is justified.
