# Adversarial test matrix — CMP-RUNTIME-PLACEMENT-CONTRACT

- `ADV-PLAC-001`: NaN/±∞ intent rotation/offset/depth → reject.
- `ADV-PLAC-002`: zero/negative dimension ratios → reject.
- `ADV-PLAC-003`: contradictory depth relation/offset → reject.
- `ADV-PLAC-004`: non-uniform scale plus coverage → reject.
- `ADV-PLAC-005`: dimension plus coverage → reject.
- `ADV-PLAC-006`: NaN solution transform point → reject.
- `ADV-PLAC-007`: frozen contract mutation → reject.
- `ADV-PLAC-008`: public/legacy identity → canonical owner only.
- `ADV-PLAC-009`: dependency graph → no new SCC.
- `ADV-PLAC-010`: exact duplicate audit → no new duplicate group.
- `ADV-PLAC-011`: production normal/boundary/interaction render → unchanged hashes.
- `ADV-PLAC-012`: solver benchmark → no material regression from ownership extraction.
