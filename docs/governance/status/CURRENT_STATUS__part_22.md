# Current status — V1.78

## V1.78 — Face visual calibration

Fresh production artifact sampling exposed four concrete visual issues in the default HumanFace slice: eye/ear center-line drift, an overly high nose bridge, insufficient nose/mouth clearance, and a hair silhouette that read as a rigid cap.

Corrections are bounded to existing face component owners. Eye/ear default anchors now share the same local Y. The nose bridge starts below eye-center level and the default mouth is lower. Hair now uses a tapered silhouette, central fringe, side locks preserving the existing hair/ear optical relation, and bounded optional strand detail controlled by `strand_density`.

Real variation sampling covers eye shape/detail, hair form/detail, face form and authored colors. Production normal, ±30° boundary and zoom interaction cases were rerendered.

Status: `V1.78 / FACE-VISUAL-CALIBRATION / CERTIFIED` only after dedicated tests, affected regression, full regression, compileall, dependency review, visual QA, truth/line-range validation, artifact purge and ZIP integrity.

## V1.79 — Face structural granularity audit

The V1.78 visual board was re-opened. The corrected Hair result is accepted only as a bounded silhouette/detail prototype; it is not evidence of true hair anatomy. The V1.79 read-only audit therefore maps recursive face granularity before further Hair geometry work.

The audit verified real owners for HumanFace, embedded HeadGeometry, Nose, Mouth, Ear, Hair, HairComposite and HairDepth. It identified missing traceability for the real Nose micro-component and created `docs/components/face/nose/`. It also records CranialVolume, ScalpBoundary, Hairline, HairMassSections, HairStrands and OralRegion as PLANNED only.

No runtime/source geometry, COLOR, cache, persistence or renderer semantics were changed.

## V1.80 — Ear input-boundary hardening

The complete V1.79 checkpoint audit was repeated before selection. Nose was excluded because it was the V1.79 scope; Hair structural children remain planned. The existing Ear leaf was selected because its owner, parent, real production consumers, cache path, persistence path and focused tests are already evidenced.

V1.80 hardens only `src/visual_engine/components/face/ear.py`: malformed width/height values bypassing the normal `Parameter` constructor are now rejected when non-numeric, boolean or non-finite. Valid production geometry is unchanged. No COLOR, database, renderer, cache policy or Hair architecture change was introduced.

Status: `V1.80 / EAR-INPUT-HARDENING / CERTIFIED` only after component gate, hostile tests, integration, full regression, compileall, dependency review, benchmark, visual invariance inspection, documentation validation, purge and ZIP integrity.
