# Component truth — CMP-RUNTIME-VISIBILITY-BOOLEAN-001

## Identity

- ID: `CMP-VBOOL-001`
- Version: V1.75
- Owner: `src/visual_engine/runtime/visibility_boolean.py`
- Legacy compatibility surface: `src/visual_engine/runtime/visibility.py`
- Parent: runtime visibility infrastructure
- Children: none
- Siblings: `region_geometry`, `coverage`, `visibility_attribution`

## Responsibility

Own the immutable `BooleanOperation`/`BooleanResult` contracts and public planar union,
intersection and difference operations over `GeometryContract` values.

## Non-responsibility

No region materialization ownership, depth ordering, optical transmission, visibility event
emission, renderer/session lifecycle, COLOR, cache, fingerprint, provenance or persistence/database.

## Owner guarantee

There is one canonical implementation owner. Historical `runtime.visibility` imports remain
compatible through re-export; `runtime.__init__` imports the canonical owner directly.
