# Guarantees and status

Guarantees after V1.70 certification:
- one canonical owner for the production face render request pipeline;
- one canonical immutable `ProductionRenderResult` contract owner;
- parent session remains graph/cache/lifetime owner;
- existing geometry/appearance/renderer/relation owners remain canonical;
- public `ProductionRenderSession.render_face` behavior is preserved;
- no COLOR/database/persistence/cache-policy/fingerprint semantic change;
- production SVG/camera/visibility identity versus V1.69 is proven for the release matrix.

Status: `CERTIFIED` after the V1.70 component gate, regression, visual QA, documentation, purge and ZIP checks.
