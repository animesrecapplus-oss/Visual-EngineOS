# Dependencies and consumers

## Canonical dependencies

`src/visual_engine/runtime/resolution_context.py:6-7` imports only `VisualEffect` and `StateActivation`.
The owner does not import the legacy `runtime.contract` facade.

## Real consumers

- `production_face_render.py:17` — production request input.
- `production_render_session.py:6` — public session input annotation.
- `production_visual_styles.py:13` — style-resolution input.
- `consequence_bindings.py:175-191` — lazy compatibility consumer retained to avoid changing its established cycle boundary.
- `runtime/contract.py:27` — compatibility re-export.
- `runtime/__init__.py:7-8` — canonical public export.

`versioning.context_fingerprint()` consumes the contract structurally and remains the fingerprint owner; it is not changed here.

## Persistence / database

No persistence or PostgreSQL consumer was found. No migration is justified.
