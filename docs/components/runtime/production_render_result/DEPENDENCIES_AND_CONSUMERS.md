# Dependencies and consumers

## Dependencies

The value contract references `ResolvedComponent`, `GeometryGenerationResult`, `GeometryContract`,
`ProductionVisibilityResolution`, `ProductionHairEarOcclusion` and `ProductionHeadEarOcclusion`.

## Real consumers

- `production_face_render.py:38-95` — producer and return annotation.
- `production_slice.py:6` — compatibility import surface.
- `runtime/__init__.py:253,262` — public runtime export.
- `tests/unit/test_v167_production_face_render.py` — production behavioral consumer.

## Persistence / database

No persistence or PostgreSQL consumer exists for this value contract. No schema or migration is justified.
