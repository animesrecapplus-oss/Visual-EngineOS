# Decision register — V1.57

## D-113 — HumanFace Hair production family

Hair is selected because the certified V1.56 HumanFace authoring graph already contains a real Hair child and the production session is the downstream consumer boundary. No domain-resolution consumer was invented.

## D-114 — bounded Hair geometry

V1.57 implements one closed cap only. Strands, follicles, morphology, accessories and expression deformation remain separate responsibilities.

## D-115 — renderer role

Hair receives an explicit renderer role instead of being mislabeled as `head`. Priority 5 places it after structural head paint and before default detail roles without introducing negative depth.

## D-116 — compatibility

The V1.56 ear-inclusive generator remains explicitly callable. Only the default production request advances to the Hair-inclusive generator.

## D-117 — COLOR/database frozen

No new COLOR downstream consumer or persistence schema consumer was demonstrated; both remain unchanged.

## D-118 — benchmark evidence

The certified V1.56 benchmark artifact, not conflicting prose, is the performance baseline. V1.57 measured +7.686% warm render change; no speculative optimization is introduced.

## V1.66 decisions

`D-119` — The V1.66 seam is the existing production geometry registry/service lifecycle; no new production consumer is invented.

`D-120` — `ProductionRenderSession` remains the canonical GeometryCache/ResolutionCache owner. This was preserved after historical ownership
tests rejected the initial broader extraction.

`D-121` — The new `ProductionGeometryServiceResources` owner receives an already-created GeometryCache and never clears it.

`D-122` — No public runtime export is added for the internal resource owner; compatibility surface remains unchanged.

`D-123` — COLOR, database, persistence, cache policy, fingerprint algorithms and geometry generation semantics remain frozen.

## V1.67 decisions

`D-124` — Select the existing end-to-end production face render request as the next independent responsibility because the fresh V1.66 audit proves it is the remaining orchestration seam in `ProductionRenderSession.render_face`.

`D-125` — Move immutable `ProductionRenderResult` assembly with that request owner and retain the old `production_slice` import path as a compatibility re-export.

`D-126` — Keep graph, GeometryCache, ResolutionCache and service-resource lifetime in `ProductionRenderSession`; the new owner receives injected resources only.

`D-127` — Do not export the internal `render_production_face` helper through `runtime.__init__`.

`D-128` — No COLOR, database, persistence, cache-policy or fingerprint semantic change is authorized by V1.67 evidence.

## V1.68 decisions

`D-129` — Select `ResolutionContext` as the next seam because the fresh V1.67 audit proves an independent immutable input contract with four real production consumers.

`D-130` — Extract only `ResolutionContext`; leave `ResolutionTrace`, `ResolvedComponent` and resolver execution in `runtime.contract`.

`D-131` — Preserve `runtime.contract.ResolutionContext` identity as a compatibility re-export while direct production consumers use the canonical owner.

`D-132` — Keep `consequence_bindings` lazy import unchanged because its established compatibility boundary already avoids a cycle and no semantic migration is required.

`D-133` — Freeze COLOR, database, persistence, cache policy and fingerprint algorithms for V1.68.

## V1.69 decisions

`D-134` — Select the immutable `ResolvedComponent` result envelope only after the fresh V1.68 consumer/ownership audit proved a distinct result-contract boundary.

`D-135` — Move `ResolutionTrace` with `ResolvedComponent` because it is a value field of the same immutable result contract; do not create a second production owner in the same brick.

`D-136` — Keep resolver execution, state/effect policy, provenance, fingerprint calculation and cache policy in their existing owners.

`D-137` — Preserve `runtime.contract.ResolvedComponent` and public `runtime` identity-compatible re-exports while direct production output typing uses the canonical owner.

`D-138` — Freeze COLOR, database, persistence, cache policy and fingerprint algorithms for V1.69.

## V1.70 decisions

`D-139` — Audit `resolve_component_contract` first, but reject that extraction after the compatibility re-export created
a new `runtime.contract ↔ runtime.resolve_component_contract` cycle. Do not hide it with dynamic coupling or duplicate code.

`D-140` — Select `ProductionRenderResult` instead because the fresh V1.69 audit proves one independent immutable output
contract with real production, public and compatibility consumers.

`D-141` — Move only the result dataclass to `runtime/production_render_result.py`; keep production request orchestration
in `production_face_render.py`.

`D-142` — Preserve `production_slice.ProductionRenderResult` and `runtime.ProductionRenderResult` as identity-compatible
imports of the canonical owner.

`D-143` — Preserve the existing nine-field order because the producer currently uses positional construction.

`D-144` — Freeze COLOR, database, persistence, cache/fingerprint algorithms and renderer semantics for V1.70.
