# Current status — V1.66

## V1.66 — Production geometry service lifecycle extraction

Fresh V1.65 audit identified one existing independent responsibility inside `ProductionRenderSession`: construction and teardown of the
production face geometry registry plus `CachedGeometryGenerator` around the session-owned `GeometryCache`.

Implemented `CMP-RUNTIME-PRODUCTION-GEOMETRY-SERVICE-RESOURCES` at
`src/visual_engine/runtime/production_geometry_service_resources.py:11-39`. The production session remains the canonical cache owner.

A first broader resource extraction was rejected by real V1.42/V1.43 ownership tests. The impact audit was reopened; cache construction
and ownership were returned to `production_slice.py`. Only registry/service lifecycle remains extracted.

Focused V1.66: 4/4 PASS. Final deterministic regression: 138 test files / 1105 collected / 1104 PASS / 1 expected PostgreSQL skip /
0 FAIL. PostgreSQL live verification is not claimed without `VISUAL_ENGINE_POSTGRES_DSN`.

Exact V1.65→V1.66 five-case identity is PASS: SVG SHA-256, camera geometry, visibility, geometry-cache statistics and resolution-cache
statistics are identical. Visual QA was generated from the real production path and inspected.

Benchmark: 3 fresh processes × 12 samples/version; measured median-of-run-medians change is recorded as measurement only and is not a
performance non-regression claim. No COLOR semantic change, database migration, persistence consumer, cache-policy change or fingerprint
algorithm change.

Status: `V1.66 / PRODUCTION GEOMETRY SERVICE LIFECYCLE EXTRACTION / BEHAVIOR IDENTITY PASS / VISUAL IDENTITY PASS / CERTIFIED`
