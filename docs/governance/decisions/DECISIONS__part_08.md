# Decision register — V1.71

`D-145` — Re-audit `resolve_component_contract` first; keep the extraction rejected because a static compatibility facade creates a new `runtime.contract ↔ runtime.resolve_component_contract` cycle. No dynamic import or duplicated resolver is allowed to conceal it.

`D-146` — Select `ProductionRenderSession` because the fresh V1.70 audit proves one existing lifecycle responsibility with a bounded owner, public consumer, compatibility consumer and real production-path integration tests.

`D-147` — Extract only `ProductionRenderSession`; `production_face_render` remains request-orchestration owner and `production_geometry_service_resources` remains service-resource owner.

`D-148` — Preserve `production_slice.ProductionRenderSession` as an identity-compatible compatibility import and move the public `runtime` export to the canonical owner.

`D-149` — Preserve session-created versus injected cache ownership semantics, graph freshness/refresh behavior, resource teardown and context-manager semantics exactly.

`D-150` — Freeze COLOR, database, persistence, cache/fingerprint algorithms and renderer semantics for V1.71.

`D-151` — Re-audit `resolve_component_contract` first for V1.72; keep it rejected because static compatibility ownership creates the same cycle. No dynamic import or duplicate resolver is allowed.

`D-152` — Select `StateActivation` and `StateDecision` as one immutable state-policy value-contract responsibility because the existing resolver facade is a real consumer and the contract can be isolated without changing state algorithms.

`D-153` — Keep `state_policy.py` as resolver owner and compatibility facade; preserve existing public import identities rather than rewiring unrelated consumers.

`D-154` — Freeze COLOR, database, persistence, cache policy, fingerprint algorithms, geometry and renderer semantics for V1.72.
