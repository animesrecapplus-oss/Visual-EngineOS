<!-- Refactored from docs/governance/roadmap/ROADMAP__part_01.md; source lines 650-791; content preserved. -->
<!-- Part 6/16. Use the family index for navigation. -->
## V1.3 — A0 correctness hardening checkpoint — 2026-09-15

This checkpoint supersedes ambiguous checkbox interpretation in older historical sections.
The following are now verified at runtime:

- [x] global visibility aggregation agrees with per-region visibility when no front occluder exists
- [x] legacy coverage delegates to overlap-safe visibility semantics
- [x] geometry cache fingerprint includes authored geometry input
- [x] extreme ocular gaze can reach the actual aperture boundary and is clipped by the eye aperture
- [x] closed/covered eyes suppress default lash emission
- [x] brow/eye gap has explicit hard bounds independent of expression presets
- [x] final eye contour data matches the resolved gaze-follow aperture

Still open by design:

- [ ] projected external shadow geometry from arbitrary occluders onto target semantic regions
- [ ] component-level shadow response across sclera/iris/pupil/highlight/lids
- [ ] production eyelid anatomy solver
- [ ] deep iris/pupil/lash/brow morphology systems
- [ ] production facial expression solver
- [ ] live PostgreSQL migration/version/round-trip integration
- [ ] quantitative visual regression and perceptual acceptance gates

A0 is a hardening checkpoint, not a declaration that V1.3 is production-complete.

## A0 structural closure tranche — 2026-09-15

Completed in the current checkpoint:
- [x] `RuntimeGraph` lifecycle contract: compiled topology index, immutable indexes, stale detection, explicit rebuild.
- [x] PostgreSQL migration lifecycle: ordered/idempotent/transactional migration runner with `schema_versions` ledger and gap detection.
- [x] PostgreSQL repository lifecycle: explicit migration/current-version operations and committed entity round-trip path.
- [x] Eyebrow/closed-eye reference-frame correction: brow no longer inherits collapsing visible aperture height.
- [x] Deterministic ocular closure QA artifacts and manifest.

Still open and deliberately separate:
- [ ] A3 definitive geometry fingerprint contract closure.
- [ ] A4 ENGINE_VISION / ARCHITECTURE_CONTRACT / ROADMAP / STATUS reconciliation.
- [ ] A5 complete visual QA reproduction pipeline.
- [ ] A6 version policy stabilization.
- [x] A8 generic end-to-end vertical slice (offline).
- [ ] A9 adversarial/property-style suite.
- [ ] A10 second full audit.

## A0 structural closure re-audit 2 — 2026-09-15

The previous A0 closure checkpoint was reopened after a migration-runner audit found that the
initial migration could be recorded without its SQL executing. This has now been corrected.

- [x] Every missing PostgreSQL migration executes before its ledger row is committed.
- [x] PostgreSQL migration checksums detect changed historical SQL.
- [x] PostgreSQL migration runner rejects unknown, gapped and checksum-less legacy histories.
- [x] RuntimeGraph rejects malformed cycles, repeated component objects and parent-link mismatch.
- [x] Rendered brow geometry is regression-tested across normal/closed eye states.
- [x] Deterministic A0 ocular QA reproduced with identical hashes.
- [ ] Live PostgreSQL server validation — requires a real PostgreSQL DSN/server and is **not** claimed complete.

The strict live gate is `tools/verify_live_postgres.py`; unlike the normal optional integration
pytest, it exits non-zero when the environment is not configured.


## V1.3 — A3 definitive geometry fingerprint closure — 2026-09-15

**Status: implemented and verified.**

The geometry fingerprint was already implemented in the geometry-cache checkpoint. A3 closed
the remaining contract ambiguity rather than creating a second fingerprint system. The local
fingerprint now has an explicit versioned payload and deterministic input-domain validation;
the dependency fingerprint carries the same contract boundary. Included/excluded fields and
adversarial canonicalization cases are covered by tests.

- [x] authored geometry participates in local identity
- [x] generator-derived geometry inputs are explicit through cache-input projection
- [x] visual/appearance/transform exclusions are explicit
- [x] component ID is separated from local recipe identity
- [x] unordered/cyclic/unsupported fingerprint inputs fail closed
- [x] contract version and algorithm are explicit
- [x] dependency fingerprint uses the same contract boundary

Next structural gate: A4 documentation/vision/roadmap/status reconciliation.

## V1.3 — A5 reproducible visual QA closure — 2026-09-16

**Status: implemented and verified.**

A5 was audited against the A4 checkpoint before implementation. The previously existing
`tools/qa_a0_closure.py` proved only a narrow A0 ocular subset and did not restore the full
feedback matrix or its reproduction source. The A5 tranche therefore closes the actual
traceability gap rather than duplicating the existing A0 generator.

- [x] complete ocular morphology matrix (9 public morphology cases)
- [x] complete gaze matrix (9 public gaze directions)
- [x] lash-form matrix (4 forms)
- [x] full public eyebrow semantic matrix (12 variants)
- [x] gaze/lid follow matrix (5 controlled cases)
- [x] pupil glow/smoke on light and dark backgrounds
- [x] reference-oriented presets with explicit non-pixel-identical wording
- [x] bilateral inward-brow case
- [x] deterministic SVG + CairoSVG PNG generation
- [x] content SHA-256 manifest excluding itself
- [x] stale-output cleanup before every generation
- [x] strict archived-manifest verification
- [x] two independent clean-generation comparison
- [x] regression tests for archive/source integrity

A5 deliberately does **not** claim artistic acceptance, anatomical correctness, production rendering,
perceptual similarity scoring, or physical optical correctness. Those remain separate technical or
visual gates.


## V1.3 — A6 version policy stabilization — 2026-09-16

**Status: implemented and verified.**

A6 was first audited against the A5 checkpoint. It was **not** already complete: the
repository contained three conflicting default sources (`pyproject.toml` = `1.3.5`,
package `__version__` = `1.0.0`, and `VersionStamp.engine` = `1.3.4`), while
`persistence.schema` incorrectly defaulted `engine_version` to `SCHEMA_VERSION`
(`1.0.0`). The resolution default (`12`) and serialized schema default (`2`) were
already present but not centrally owned.

A6 closes that drift without inventing a single global version number.

- [x] one canonical runtime version policy
- [x] package version derives from `ENGINE_VERSION`
- [x] `VersionStamp()` derives all three defaults from the policy
- [x] canonical entity records distinguish engine and schema versions
- [x] packaging metadata is checked against the engine version
- [x] migration ledger remains explicitly independent from semantic schema version
- [x] explicit historical `VersionStamp` overrides remain supported
- [x] structural verifier and regression tests cover cross-surface drift

The change does **not** advance the resolution version because A6 changes version ownership,
not resolution semantics. It also does not claim live PostgreSQL verification.

### Verification

```text
python tools/verify_a6_version_policy.py  PASS
python -m pytest -q                       PASS
python -m compileall -q src tests         PASS
```
