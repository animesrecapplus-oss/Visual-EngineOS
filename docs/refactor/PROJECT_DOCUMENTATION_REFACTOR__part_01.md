# Documentation / evidence architecture refactor — 2026-09-30

## Objective

Refactor the V1.47 checkpoint so documentation can be located by concern/component/micro-component, every documentation and release-manifest text file is at most 150 lines, generated evidence is version-scoped, and stale root-level release metadata is eliminated without inventing or silently rewriting historical facts.

## Verified starting state

- V1.47 certified checkpoint: 763 files.
- `docs/`: 133 source documents, including a 5,401-line machine-readable eye blueprint.
- `IMPLEMENTATION_LOG.md`: 2,595 lines.
- `ROADMAP.md`: 2,112 lines.
- `DECISIONS.md`: 1,406 lines and contained a duplicated 925-line vision prefix.
- `ENGINE_VISION.md`: 1,083 lines.
- Release manifests V1.36–V1.47 were stored at repository root; several were 3,500–4,000 lines.
- 126 Python files in `src/tests/tools` exceeded 150 lines; these are runtime/test architecture, not documentation, and were not blindly split in this documentation brick.

## New documentation architecture

- `docs/governance/` — authoritative vision, architecture, roadmap, decisions, current status.
- `docs/components/eyes/` — ocular component and micro-component contracts, blueprint, morphology, reference/calibration.
- `docs/runtime/` — generic foundations, geometry, placement, visibility, appearance, cache and production contracts.
- `docs/domains/color/` — COLOR contracts and historical implementation records.
- `docs/history/` — frozen historical foundations and implementation logs.
- `docs/refactor/` — structural audits, policy and migration records.

## Long-document policy

Markdown/text/JSON documentation files are now <=150 lines. Long Markdown documents are split at semantic headings or paragraph boundaries and retain source line ranges in part headers. The V1.4 machine blueprint is split into bounded JSON metadata, stream files and ordered task chunks.

## Duplicate cleanup

- The duplicated vision prefix was removed from the master implementation log and decision register; the canonical vision remains in `docs/governance/architecture/`.
- Empty `__init__.py` package markers were audited and retained because they are package markers, not duplicate implementation.
- Repeated historical verifier helpers were not globally merged: they belong to checkpoint-specific tooling. Shared document/blueprint/release-manifest loaders were introduced where behavior is identical and migration-safe.
- Byte-identical historical visual outputs referenced by release manifests were retained; deleting them would invalidate certified manifest coverage.

## Release/evidence placement

- Root release manifests/evidence are gone.
- `artifacts/releases/vX.Y/` contains the immutable release record.
- Large release manifests are bounded into `manifest.json` + metadata + ordered entry chunks.
- `tools/release_manifest.py` reconstructs the original canonical bytes and verifies the recorded SHA-256.
- Current V1.47 generated evidence lives only under `artifacts/current/v1.47/`.
- Superseded generated evidence is under `artifacts/history/vX.Y/`.

## Machine-contract preservation

The split V1.4 blueprint loader reconstructs the original object exactly: 285 tasks and 17 streams, with `load_blueprint() ==` the pre-refactor JSON object. Release-manifest reconstruction was checked for every V1.36–V1.47 release record and matched its pre-refactor SHA-256.

## Tests / verification

- 111 test files.
- 956 collected tests.
- 955 passed.
- 1 expected PostgreSQL skip.
- 0 failures.
- All 12 isolated test batches completed successfully; the V1.4 batch required 23.2 s when run separately after the overall batch window expired.
- `compileall -q src tests tools`: PASS.
- Documentation reference audit: 0 broken `docs/...` references.
- V1.47 production visibility gate: PASS.

## Important nonclaim

The 150-line discipline is now enforced for documentation and release-manifest text. Source-code modularization is deliberately a separate engineering brick because splitting runtime modules without responsibility-level contracts would be architectural surgery, not housekeeping.

## Next micro-scope

Create a dedicated source-code modularization audit: select only modules whose responsibilities are demonstrably separable, extract one responsibility at a time, preserve public contracts, run focused + full regressions, and only then address repeated helpers that are proven to be the same abstraction. Do not split a runtime file merely to satisfy a line count.

## Exact code/test change coordinates

- `tools/document_loader.py`: 1–33 — new bounded-document resolver.
- `tools/eye_blueprint_loader.py`: 1–26 — new exact V1.4 blueprint reassembler.
- `tools/release_manifest.py`: 1–45 — new split-release-manifest loader/reconstructor.
- `tools/audit_v137_color_consumer.py`: 16–18, 25, 41 — consumes the split V1.36 manifest through the loader.
- `tools/verify_a4_docs.py`: 11–13, 20 — resolves split documentation.
- `tools/verify_a10_full_audit.py`: 15–17, 94–100, 113–119, 249 — resolves split documentation.
- `tools/verify_v147_production_visibility.py`: 9 — current V1.47 evidence path.
- `tools/audit_v147_production_visibility.py`: 13 — current V1.47 evidence path.
- `tools/benchmark_v147_visibility.py`: 16 — current V1.47 evidence path.
- `tools/visual_qa_v147_visibility.py`: 27 — current V1.47 evidence path.
- `tests/unit/test_v14_eye_blueprint.py`: 4, 10, 19 — split blueprint loader.
- `tests/unit/test_v13_a5_visual_qa.py`: 4, 9–10, 17, 24 — split-document resolution.
- `tests/unit/test_v144_production_vertical_slice.py`: 13–15, 21, 29 — split V1.44 report resolution.
- `src/visual_engine/components/face/eyes/README.md`: 22–24 — new blueprint/document paths.
- `README.md`: rewritten as a 39-line navigation entry point.

Additional historical verifier/visual-QA files were changed only where their checked-in document/artifact path moved; no production `src/visual_engine/**/*.py` implementation was changed by this refactor.

## Machine evidence

`artifacts/current/v1.47/V1.47_DOCUMENTATION_REFACTOR_EVIDENCE.json` records the final structural counts, blueprint equivalence, release-manifest reconstruction hashes, test matrix and source-change boundary.
