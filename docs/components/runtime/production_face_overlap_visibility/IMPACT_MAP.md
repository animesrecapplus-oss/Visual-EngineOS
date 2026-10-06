# Impact map

Affected:
- `src/visual_engine/runtime/production_face_overlap_visibility.py:1-111` — new canonical owner.
- `src/visual_engine/runtime/production_face_overlap_relations.py:11,33-61` — import and existing consumer call; owner extraction is delegated to the canonical V1.62 module.
- `src/visual_engine/runtime/__init__.py:247-256` — public export.
- `tests/unit/test_v160_production_face_overlap_visibility.py:1-76` — extraction and hostile tests.

Unaffected by design:
- generic visibility and attribution algorithms;
- geometry generators;
- renderer output;
- cache/fingerprint algorithms;
- persistence/database;
- COLOR;
- Hair/Ear and Head/Ear contracts.
