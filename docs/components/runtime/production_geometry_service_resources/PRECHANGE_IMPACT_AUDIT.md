# Pre-change impact audit

## Initial audit

`IMP-GSR-001`: `ProductionRenderSession` mixed graph lifecycle, cache ownership, geometry service construction,
render orchestration and relation calls. The registry/service pair was an independent existing responsibility.

## Re-opened audit

The first implementation moved cache construction into the new resource owner. Batch 11 of the final regression
failed two historical ownership tests (`test_v142_resolution_cache_lifetime` and `test_v143_production_consumer_audit`).
This was a new architectural fact, not a test to bypass.

The audit was reopened. Cache construction/ownership was returned to `production_slice.py`; only registry/service
construction and teardown remained in the new owner. The failing batch and all remaining final batches were rerun.

## Final scope

One module, one responsibility: production geometry registry/service lifecycle around a caller-owned cache.
No COLOR, persistence, database, fingerprint, cache-policy, renderer or generation-algorithm change is authorized.
