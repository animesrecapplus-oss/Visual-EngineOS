# Roadmap — V1.67 and next frontier

## V1.67 — Production face render orchestration extraction

Fresh V1.66 audit proved one remaining independent production responsibility: the existing end-to-end face render request orchestration
inside `ProductionRenderSession.render_face`.

Implemented one owner only:
- `CMP-RUNTIME-PRODUCTION-FACE-RENDER` → `runtime/production_face_render.py:1-108`.
- The parent session retains graph/cache/resource lifetime and public API compatibility.
- Existing resolution, geometry, transform, visual-style, renderer and relation owners remain canonical.

Historical architectural source-location tests were updated only where they asserted the former owner location; all affected tests pass.

## V1.68 rule

Start from the fresh certified V1.67 checkpoint. Perform a read-only audit first. Do not assume the renderer implementation, COLOR,
cache, persistence, or another result-contract seam is next without new real consumer/owner/contract/impact proof.
