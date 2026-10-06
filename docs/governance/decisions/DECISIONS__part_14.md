# Decision register — V1.78

`D-181` — Treat user-reported visual defects as production QA findings requiring sampled artifacts, not as subjective comments to be ignored.

`D-182` — Encode eye/ear same-Y alignment as the HumanFace default aesthetic only; do not promote it to a universal anatomical constraint.

`D-183` — Correct nose/mouth spacing in the face entity and nose geometry owner rather than changing generic placement or renderer semantics.

`D-184` — Replace the flat hairline with tapered silhouette, fringe, side locks and bounded strand detail; preserve the existing hair depth layer so hair/ear optical ownership remains valid.

`D-185` — Require real variation sampling across form, color and detail controls before claiming visual QA PASS for this face slice.

## D-185 — V1.79 face granularity boundary and horizontal progression

Do not deepen Hair from the V1.78 cap-like silhouette by adding more cosmetic detail. First establish the upstream structural boundary as a future micro-component only when a real consumer exists. Treat `ScalpBoundary`, `Hairline`, `HairMassSections`, `HairStrands` and `OralRegion` as PLANNED, not IMPLEMENTED.

The Head remains an embedded `HEAD` surface owned by `components/face/generators.py`; creating a standalone Skull/Head owner without a real consumer would violate the no-speculative-abstraction rule.

The missing Nose truth dossier is the mature horizontal scope for V1.79 because Nose already has a production owner and real consumers. The source geometry remains unchanged.

## D-186 — V1.80 horizontal selection: Ear

Select the existing `Ear` leaf as the V1.80 mature micro-component. It has a real owner and production consumer chain, unlike the proposed Hair structural children. Do not reuse Nose immediately after its V1.79 traceability closure. V1.80 changes only the Ear input boundary and preserves valid geometry and all existing visual/architectural semantics.

## D-187 — Hair proposal remains non-implementation

Keep `cranium → scalp boundary → hairline → masses → sections/locks → strands → density → flow → depth/occlusion` as architectural planning metadata. No proposed Hair child becomes `IMPLEMENTED` without its own owner, consumer, contract, invariants, tests, impact and evidence.
