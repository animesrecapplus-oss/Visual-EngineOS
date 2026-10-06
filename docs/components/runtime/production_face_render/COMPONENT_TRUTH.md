# Component truth

`CMP-RUNTIME-PRODUCTION-FACE-RENDER`.

`FILE-PFR-001`: canonical owner source is `src/visual_engine/runtime/production_face_render.py`.
`TST-PFR-001`: focused production-face-render suite is the direct behavioral gate.

## Responsibility

Own the existing end-to-end orchestration of one production face render request and assembly of the
`ProductionRenderResult` value supplied by its canonical result-contract owner.

## Explicit non-responsibility

- ownership of the `ProductionRenderResult` class itself;
- session/cache/graph lifetime or ownership;
- geometry algorithms or geometry-cache policy;
- generic appearance/COLOR semantics;
- spatial-transform algorithms;
- SVG renderer implementation;
- visibility/occlusion/attribution algorithms;
- persistence/database;
- fingerprint algorithms;
- request lifetime beyond one render call.

Existing specialized owners remain canonical; this component orchestrates their real calls and does not reconstruct
result-contract semantics.
