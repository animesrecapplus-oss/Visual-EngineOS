# Dependencies and consumers

## Direct dependencies

- `Component` — root type boundary.
- `RuntimeGraph` — topology snapshot and freshness/rebuild boundary.
- `GeometryCache` / `ResolutionCache` — explicit cache lifetime boundary.
- `ProductionGeometryServiceResources` — geometry service lifecycle tied to the session's geometry cache.
- `render_production_face` — canonical request-orchestration owner.
- `ResolutionContext`, `VersionStamp`, placement/camera/theme contracts — request inputs.

## Real consumers

- `src/visual_engine/runtime/production_slice.py:7` — compatibility import.
- `src/visual_engine/runtime/__init__.py:254` — public API export.
- `tests/unit/test_v145_production_vertical_slice.py:29-113` — historical production-session boundary and lifecycle integration tests.
- `tests/unit/test_v166_production_geometry_service_resources.py:27-47` — cache/resource ownership integration tests.
- `tests/components/runtime/production_render_session/test_v171_production_render_session_truth.py:1-86` — dedicated owner/hostile/production-path tests.

The actual production path is entered through this public session and delegates to `production_face_render.py:38-95`; no second session owner exists.

## Persistence / database

No persistence or PostgreSQL consumer exists for the session lifecycle contract. No schema or migration is justified.
