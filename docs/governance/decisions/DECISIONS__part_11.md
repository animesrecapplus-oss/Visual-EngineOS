# Decision register — V1.75

`D-165` — Select `CMP-RUNTIME-VISIBILITY-BOOLEAN` because planar boolean composition is a distinct responsibility with its own immutable contract and public API inside `runtime.visibility`.

`D-166` — Make `runtime/visibility_boolean.py` the canonical owner while preserving historical `runtime.visibility` names and public identity.

`D-167` — Reopen impact after the first implementation produced a +11.941% fresh-process hot-path regression; do not route `resolve_visibility` through new Python helper calls.

`D-168` — Freeze depth, optical transmission, event emission, region materialization, cache/fingerprint/provenance, persistence/database, COLOR and renderer semantics.

`D-169` — Require final benchmark and production visual identity evidence before certification.
