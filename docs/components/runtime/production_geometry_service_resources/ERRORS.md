# Errors and corrections

`ERR-GSR-001`: initial V1.66 draft moved `GeometryCache`/`ResolutionCache` construction into the new resource
owner. Final regression exposed existing V1.42/V1.43 ownership contracts requiring the production session to remain
the canonical production cache owner. The impact analysis was reopened and the scope was narrowed to registry/service
lifecycle only. The failing batch was rerun and passed.

`ERR-GSR-002`: the first behavior evidence tool compared `repr(session.geometry_cache.stats)` (bound method) instead
of `stats()`, producing a false evidence delta. The tool was corrected and the identity comparison rerun successfully.

`ERR-GSR-003`: the first visual QA producer lacked the runtime imports and failed before evidence generation. Imports were
added and the full visual QA was rerun successfully.

`ERR-GSR-004`: the first benchmark configuration (5 fresh processes × 30 samples) exceeded the execution window. It was
reduced to 3 fresh processes × 12 samples; the final report explicitly remains measurement-only.
