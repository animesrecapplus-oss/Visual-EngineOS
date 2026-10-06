# V1.80 — micro-component selection and audit

## VERIFY result

Checkpoint: certified V1.79 ZIP `visual_engine_v1.79_face_granularity_CERTIFIED.zip`; SHA-256 `8a865d191defc13e3a670eecf1f50d9088c0c79c9d4fc5b1dfc864d9274484a4`. ZIP integrity: PASS.

V1.79 truth, roadmap, architecture, decisions, protocol and artifact policy were reread. The V1.79 artifact set contains only the current brick evidence. The extracted checkpoint contains no runtime/source changes relative to its certification evidence. The working tree has no Git metadata, so cleanliness is established by checkpoint extraction, source/DB identity comparison and generated-file purge rather than `git status`.

## Selection matrix

| Candidate | Evidence | V1.80 decision |
|---|---|---|
| Nose | real owner + consumers; selected for V1.79 dossier | EXCLUDE: immediately previous scope |
| Mouth | real owner + production composite + tests | DEFER: no justified new leaf contract identified |
| Ear | real owner + production composite + cache + persistence + focused tests + existing relation consumers | **SELECT** |
| Hair | real coarse owner but upstream scalp/hairline boundaries remain planned | EXCLUDE from geometry deepening |
| Hair proposed children | no standalone owner/consumer | PLANNED only |
| Cranial/Scalp/Oral regions | no standalone owner/consumer | PLANNED only |

## Selected micro-component

`CMP-FACE-EAR` — existing `Ear` leaf generator, `src/visual_engine/components/face/ear.py`.

V1.80 responsibility: reject malformed numeric width/height values that bypass the normal `Parameter` constructor. It does not change valid geometry, ownership, renderer policy, COLOR, cache policy or database schema.

## Hair boundary preservation

The proposed sequence `cranium → scalp boundary → hairline → masses → sections/locks → strands → density → flow → depth/occlusion` remains a design proposal. V1.80 does not declare any of these as implemented and does not create speculative source directories.
