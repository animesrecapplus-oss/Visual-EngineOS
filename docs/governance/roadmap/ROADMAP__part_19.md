# Roadmap — V1.54

## Completed micro-scope

1. Re-read the certified V1.53 checkpoint and its domain-input truth dossier.
2. Re-audited `domain_resolution.py` instead of assuming its next seam.
3. Proved the input factory has real BASE/COLOR/MATERIAL consumers.
4. Selected exactly one responsibility: canonical input construction/normalization.
5. Created `runtime.domain_input_factory` as canonical owner.
6. Rewired real consumers while retaining historical compatibility.
7. Added hostile API, identity, cycle, duplicate and persistence-boundary tests.
8. Ran focused and complete deterministic regression.
9. Benchmarked fresh-process construction and digest access.
10. Updated a dedicated micro-component truth dossier with stable IDs and exact line ranges.
11. Purged superseded generated evidence.
12. Produced the V1.54 certification package.

## Deferred by evidence

`unresolved_domain_result()` remains in `runtime.domain_resolution`. No production consumer currently proves an independent ownership boundary, so extracting it now would be speculative.

## Next rule

Before V1.55, re-audit `domain_resolution.py` and all newly exposed consumers again. Do not infer the next responsibility from line count or from the existence of a helper.
