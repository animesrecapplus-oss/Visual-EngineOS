# Relations

`REL-PRR-001`: `ProductionRenderSession → ProductionRenderResult` — public render result boundary.
`REL-PRR-002`: `production_face_render → ProductionRenderResult` — canonical construction/return relation.
`REL-PRR-003`: `production_slice → ProductionRenderResult` — compatibility import relation.
`REL-PRR-004`: `runtime.__init__ → ProductionRenderResult` — public export relation.
`REL-PRR-005`: `ProductionRenderResult → ResolvedComponent` — contained generic resolution result.
`REL-PRR-006`: `ProductionRenderResult → GeometryGenerationResult/GeometryContract` — geometry result values.
`REL-PRR-007`: `ProductionRenderResult → visibility/occlusion value types` — existing production result values.
