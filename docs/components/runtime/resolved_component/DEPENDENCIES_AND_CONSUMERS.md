# Dependencies and consumers

## Canonical dependencies

`resolved_component.py:11-14` consumes only the generic geometry/visual contracts, provenance value,
and version/fingerprint value types.

## Real consumers

- `production_face_render.py:17` — production result annotation and request output.
- `runtime/contract.py:28` — resolver construction plus compatibility import.
- `runtime/__init__.py:7-9` — public compatibility/export surface.
- cache/resolution tests consume the produced object through `resolve_component`.

No consumer owns or reconstructs this result envelope.

## Persistence / database

No persistence or PostgreSQL consumer was found. No migration is justified.
