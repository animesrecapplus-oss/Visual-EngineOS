# Roadmap

## V1.65 completed

Fresh V1.64 audit found the remaining face-overlap orchestration in `ProductionRenderSession.render_face`.
The semantic resolver itself was already canonical and was not modified.

Implemented one bounded owner:
`src/visual_engine/runtime/production_face_overlap_relations.py:26-61`.

The adapter preserves the four already-proven generator variants and their exact occluder sets.
Unknown generators return no proof instead of silently acquiring a relation.

V1.66 must start from a fresh read-only audit of the certified V1.65 checkpoint.
No new responsibility is authorized without a new real consumer and contract proof.
