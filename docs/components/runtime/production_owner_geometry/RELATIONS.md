# Relations

`REL-POG-001`: `ProductionRenderSession.render_face` → owner extractor; session remains lifecycle owner.
`REL-POG-002`: owner extractor → `GeometryContract`; no reverse dependency into the session.
`REL-POG-003`: owner extractor → face-overlap/Head-Ear adapters and Hair/Ear orchestration through returned geometry/depth.
`REL-POG-004`: owner extractor is parallel to style resolution and visibility algorithms; it performs no appearance or occlusion calculation.
`REL-POG-005`: public runtime export points to the single canonical callable.
