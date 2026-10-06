# Relations

`REL-PVS-001`: `ProductionRenderSession.render_face` → style adapter; session remains lifecycle owner.
`REL-PVS-002`: style adapter → generic `resolve_component`; appearance inheritance/effects/fingerprint ownership remains generic.
`REL-PVS-003`: style adapter → `render_geometry_svg` indirectly through its returned mapping; renderer does not resolve Components.
`REL-PVS-004`: style adapter → camera-space `GeometryContract`; metadata identifies geometry owners without modifying geometry.
`REL-PVS-005`: style adapter is parallel to production occlusion adapters; it does not calculate occlusion.
`REL-PVS-006`: no reverse dependency from generic resolver/renderer into production session or this adapter.
