# Impact map

`IMP-PRS-001`: move the existing session class only; convert `production_slice.py` into a compatibility facade.
`IMP-PRS-002`: update the public runtime import to the canonical owner.
`IMP-PRS-003`: update historical ownership tests that correctly described the former session owner.
`IMP-PRS-004`: update affected runtime truth dossiers so consumer/parent line ranges remain exact after the move.
`IMP-PRS-005`: preserve graph, cache, resource, resolution, geometry, visibility and renderer behavior.
`IMP-PRS-006`: no cache-policy/fingerprint/provenance algorithm changes.
`IMP-PRS-007`: no COLOR semantic change and no persistence/database change.
`IMP-PRS-008`: production SVG/camera/visibility/cache identity must remain identical to V1.70.
`IMP-PRS-009`: dependency graph must add no SCC or duplicate owner.
