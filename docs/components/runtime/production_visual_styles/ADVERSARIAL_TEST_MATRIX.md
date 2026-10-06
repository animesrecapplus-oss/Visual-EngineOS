# Adversarial test matrix

`ADV-PVS-001`: wrong graph type → rejected.
`ADV-PVS-002`: empty component ID → rejected.
`ADV-PVS-003`: wrong geometry type → rejected.
`ADV-PVS-004`: wrong root visual type → rejected.
`ADV-PVS-005`: wrong context type → rejected.
`ADV-PVS-006`: unknown geometry owner → ignored, matching the former caller.
`ADV-PVS-007`: duplicate owner metadata → set-deduplicated, matching the former caller.
`ADV-PVS-008`: root-resolution duplication → guarded by exact cache-store count.
`ADV-PVS-009`: changed resolution context → delegated cache identity produces a distinct resolved visual.
`ADV-PVS-010`: deterministic repeated inputs → identical mapping and owner order.

No new NaN/∞ arithmetic, depth arithmetic, occlusion calculation, persistence path or cache mutation exists in this adapter;
those responsibilities remain delegated to their existing owners.
