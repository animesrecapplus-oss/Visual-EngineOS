# Impact map

`IMP-PFR-001`: `ProductionRenderSession.render_face` continues delegating the request pipeline.
`IMP-PFR-002`: result-class ownership moves to `CMP-RUNTIME-PRODUCTION-RENDER-RESULT`; producer construction remains here.
`IMP-PFR-003`: `ProductionRenderResult` public and compatibility identities remain unchanged.
`IMP-PFR-004`: parent/lifecycle graph, cache ownership, stale-graph guard and teardown remain in the session.
`IMP-PFR-005`: children/siblings are called without semantic modification.
`IMP-PFR-006`: cache/fingerprint behavior is unchanged.
`IMP-PFR-007`: no persistence/database path is touched.
`IMP-PFR-008`: no new downstream COLOR consumer or transformation exists.
`IMP-PFR-009`: deterministic five-case production identity remains the release gate.
`IMP-PFR-010`: production SVG/camera/visibility behavior must remain identical; visual QA is required.
