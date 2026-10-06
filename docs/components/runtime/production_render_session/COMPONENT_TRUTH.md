# Component truth

`CMP-RUNTIME-PRODUCTION-RENDER-SESSION`.

## Identity

`FILE-PRS-001`: `src/visual_engine/runtime/production_render_session.py:18-118`.
`TST-PRS-001`: `tests/components/runtime/production_render_session/test_v171_production_render_session_truth.py:1-86`.

## Responsibility

Own the caller-owned lifetime boundary for one production face render session: root/graph lifetime, injected-versus-session cache lifetime, resource teardown, stale-graph guard, refresh, context-manager semantics and delegation to the canonical request owner.

## Non-responsibility

Request pipeline semantics; generic resolution; geometry generation semantics; visual-style resolution; SVG rendering; visibility/occlusion algorithms; result-contract definition; COLOR; fingerprint algorithms; persistence/database.
