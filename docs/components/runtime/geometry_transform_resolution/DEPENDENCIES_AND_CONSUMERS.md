# Dependencies and consumers

## Real consumers

- `src/visual_engine/runtime/geometry_transform.py:5-8` — compatibility facade and geometry-contract adapter.
- `src/visual_engine/components/face/eyes/reference/transform.py:6,21,35` — eye reference consumer.
- `src/visual_engine/runtime/__init__.py:39-50` — public API surface through the facade.
- existing geometry-transform unit tests and eye transform tests — behavioural consumers.

## Dependencies

`LocalTransform`, matrix primitives, `RuntimeGraph`, `Camera`, `Placement`, and `Matrix3` only.
The owner does not import renderer, appearance, COLOR, cache or persistence code.

## Persistence / database

No persistence or PostgreSQL consumer exists. No migration or schema change is justified.
