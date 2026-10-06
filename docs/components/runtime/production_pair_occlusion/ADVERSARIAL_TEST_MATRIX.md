# Adversarial matrix

`ADV-PAIR-001`: same owner → reject.
`ADV-PAIR-002`: NaN/∞ depth → reject.
`ADV-PAIR-003`: opacity/transmission outside `[0,1]` → reject.
`ADV-PAIR-004`: non-boolean coplanar/attribution flags → reject.
`ADV-PAIR-005`: zero/ambiguous semantic regions → reject.
`ADV-PAIR-006`: coplanar relation → preserve actual depth relation in generic kernel.
