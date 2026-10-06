# Current status — V1.52

## V1.52 result-contract ownership

V1.52 starts from the certified V1.51 checkpoint and re-audits `runtime.domain_resolution` without preselecting
a seam. The selected responsibility is the immutable domain-result contract: status, resolved-field,
provenance and result-envelope types now have one canonical owner in `runtime.domain_result_contract`.

`runtime.domain_resolution` remains the owner of input construction and the compatibility facade. BASE, COLOR and
MATERIAL are verified real consumers through that facade. `domain_result_validation` remains the separate semantic
result-vs-input validator from V1.51.

## Hostile correction

The re-audit found that impossible runtime result status/container types could be accepted by the old constructor
boundary. V1.52 closes this inside the selected owner and adds explicit hostile tests. No resolver algorithm or
COLOR semantic rule changed.

## Persistence / cache / visual

No persistence/database consumer was found; no schema or migration changed. `ResolutionCache` and
`ResolutionFingerprint` are unchanged. The selected owner has no geometry/renderer operation, so independent
visual evidence is `NOT_APPLICABLE` and no synthetic image is retained.

## Verification

- 121 test files / 1007 collected / 1006 passed / 1 expected PostgreSQL skip / 0 failed.
- compileall: PASS.
- component truth gate: PASS.
- 179 modules / 423 internal edges / 3 pre-existing SCCs / 0 exact duplicate groups.
- fresh-process benchmark measured +3.604% result construction and +1.125% result-digest cost; no optimization was introduced.

## Status

`ENGINEERING PASS / ONE RESPONSIBILITY / API COMPATIBLE / HOSTILE TYPE HARDENING / CYCLE SAFE / PERSISTENCE UNCHANGED / COLOR UNCHANGED / VISUAL NOT_APPLICABLE / CURRENT EVIDENCE RETAINED`.
