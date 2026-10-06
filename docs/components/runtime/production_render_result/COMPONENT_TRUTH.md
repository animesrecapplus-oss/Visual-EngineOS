# Component truth

`CMP-RUNTIME-PRODUCTION-RENDER-RESULT`.

## Identity

`FILE-PRR-001`: `src/visual_engine/runtime/production_render_result.py`.
`TST-PRR-001`: `tests/components/runtime/production_render_result/test_v170_production_render_result_truth.py`.

## Responsibility

Own the immutable `ProductionRenderResult` output envelope returned by the production face render path.

## Non-responsibility

Request orchestration; session/cache/graph lifetime; geometry generation/transform; SVG rendering; visibility and
occlusion algorithms; generic resolution; COLOR; fingerprinting; persistence/database.
