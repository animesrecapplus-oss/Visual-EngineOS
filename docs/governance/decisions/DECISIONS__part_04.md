# D-092 — Documentation and release-evidence structure — 2026-09-30

## Decision

Documentation is organized by architectural concern, component and micro-component rather than by a single flat directory. Human-readable documentation and release-manifest text are bounded to 150 lines maximum.

## Rules

- Authoritative governance remains under `docs/governance/`.
- Component and micro-component contracts live under `docs/components/`.
- Generic runtime contracts live under `docs/runtime/`.
- Domain contracts such as COLOR live under `docs/domains/`.
- Historical records live under `docs/history/`.
- Structural refactor records live under `docs/refactor/`.
- Release manifests/evidence live under `artifacts/releases/vX.Y/`.
- Current generated evidence lives under `artifacts/current/vX.Y/`.
- Superseded evidence lives under `artifacts/history/vX.Y/`.
- Repository root is not a generated-evidence or release-metadata directory.

## Preservation rule

Historical factual records are not rewritten merely to make them prettier. Large records are split into ordered parts; machine-readable release manifests remain reconstructable byte-for-byte and retain their original SHA-256.

## Duplicate rule

A duplicate is removed only when its equivalence and non-ownership are proven. Named historical evidence that appears byte-identical but is independently referenced by a release manifest is retained because its filename is part of the certified evidence set.

## Scope boundary

The 150-line rule is applied to documentation and release-manifest text in this brick. Runtime Python modularization is a separate controlled refactor and must be driven by responsibility boundaries, public contracts and regression evidence rather than line count alone.

# D-093 — Source modularization is responsibility-driven — 2026-09-30

## Decision

The 150-line rule is a documentation discipline, not a license to split runtime code mechanically.
Runtime extraction requires a real responsibility boundary, consumer evidence, dependency safety and
regression proof.

## V1.48 application

`runtime.visibility` was split only at the renderer-independent planar-region materialization boundary.
`runtime.region_geometry` is the sole owner of that responsibility; compatibility imports preserve the
existing public API.

No second source module is extracted in the same brick. No visual feature or COLOR behavior is changed.


# D-094 — Current-only generated artifact retention — 2026-09-30

## Decision

`artifacts/` remains part of the project. It is a current validation area, not a historical archive.
Only the latest certified brick's generated evidence is retained under `artifacts/current/vX.Y/`;
superseded generated contents are purged when the next brick is certified.

The certified ZIP remains the external release boundary. Historical implementation facts stay in
documentation and are not reconstructed from deleted generated evidence.

## V1.49 application

The V1.48 interpretation that deleted the entire `artifacts/` tree is explicitly corrected. V1.49
retains `artifacts/current/v1.49/` with the current visual validation evidence only.

## D-095 — Architectural immune-system protocol and pilot — 2026-09-30

### Decision

The project adopts a mandatory component-truth, impact-analysis, hostile-review, integration and visual-execution protocol before continuing broad V1.50+ modularization.

### Rules

- Code ownership and documentation ownership follow the same semantic component path.
- Every adopted component gets a bounded truth dossier and machine-readable manifest.
- Every modification starts with multidirectional impact analysis.
- Hostile review is mandatory and distinguishes `PASS` from `DECLARED`/`BLOCKED`.
- Parent/child/sibling relations are tested explicitly; isolated correctness never implies composed correctness.
- `PROMPT → ... → RENDER → INSPECTION → DIAGNOSIS → CORRECTION → RE-EXECUTION` is mandatory whenever output can change.
- The first pilot is `face/eyes/pupil`; the repository is not mass-restructured.
- A local ownership conflict discovered by the pilot (`LashShadowSpec`) was corrected to the lashes owner while preserving legacy API identity.
- `artifacts/` remains in the project and retains only current V1.50 evidence at certification.


## D-096 — V1.51 domain-result validation ownership — 2026-09-30

### Decision

Domain-result validation becomes an independent runtime responsibility with one canonical owner. The legacy symbol remains a compatibility facade.

### Evidence rules

- real consumers must be demonstrated before extraction;
- persistence/database impact must be searched explicitly;
- a new cycle is a blocking defect even when focused tests pass;
- constructor invariants and validator invariants are tested separately;
- visual evidence is required only when the selected seam can change rendered output.

### Result

`runtime.domain_result_validation` is the sole implementation owner. No COLOR semantic implementation, database schema, renderer or cache contract changed.


## D-097 — V1.52 result-envelope ownership boundary — 2026-09-30

The immutable domain-result contract is extracted as one responsibility into `runtime.domain_result_contract`.
The compatibility surface remains in `runtime.domain_resolution`; input construction and semantic result validation
remain separate owners.

## D-098 — V1.52 hostile type hardening — 2026-09-30

The selected result-contract owner hardens its own runtime type boundaries for status, domain, field, provenance and
result containers. This closes impossible states without changing resolver algorithms, persistence, cache ownership,
renderer behavior or COLOR semantics.

## D-101 — V1.54 canonical domain-input factory ownership — 2026-10-01

The canonical construction/normalization policy for `DomainResolutionInput` is owned by `runtime.domain_input_factory`. BASE, COLOR and MATERIAL import the owner directly; `domain_resolution` remains a compatibility facade.

The factory does not own the immutable input contract, result semantics, persistence, cache/fingerprint lifecycle or rendering.

## D-102 — unresolved-result extraction remains blocked by evidence, not by implementation convenience

`unresolved_domain_result()` remains in `runtime.domain_resolution` because the V1.54 consumer audit found no production consumer proving an independent owner boundary. `DECLARED`/absence of consumer is not promoted to implementation.

# D-103 — V1.59 canonical production pair boundary — 2026-10-01

The second real production occlusion relation (HumanFace head → Ear) justifies a domain-neutral
pair adapter. Domain-specific owner-kind validation remains in Hair/Ear and Head/Ear adapters.
No generic renderer or COLOR redesign is introduced.

# D-104 — V1.59 coplanar depth semantics and attribution scope — 2026-10-01

A real Head/Ear overlap exists while both surfaces are authored at depth `0` and the renderer paints
Ear before Head. The production relation therefore uses explicit `coplanar_occludes=True`; negative
or invented depth layers are forbidden. Head/Ear does not compute causal attribution because no real
attribution consumer exists. The generic visibility result now preserves `COPLANAR` instead of relabelling
it `FRONT`.
