# Current status — V1.81

## V1.81 — Mouth input-boundary hardening

V1.81 restarted from the certified V1.80 checkpoint and repeated the read-only VERIFY audit before selecting a
new micro-component. The proposed Hair hierarchy remains planning metadata only. Ear was excluded because it was
V1.80's scope. `CMP-FACE-MOUTH` was selected because it has a real executable owner, real production consumers,
existing contracts/invariants, cache and persistence evidence, visibility relations and focused tests.

The audit reproduced a real leaf-boundary defect: bypassed `Parameter` state could be coerced through `float()`,
accepting bool/string values, while positive subnormal dimensions could collapse to zero-radius geometry.
V1.81 closes that boundary only in `src/visual_engine/components/face/mouth.py:15-27,30-59`.

Valid Mouth geometry remains unchanged. No COLOR, database, cache policy, renderer policy, composite ownership or Hair
architecture was modified.

Status: `V1.81 / MOUTH-INPUT-HARDENING / CERTIFIED` after component gate, hostile tests, integration, full regression,
compileall, source/dependency/database audits, benchmark, visual invariance inspection, truth validation, purge and ZIP integrity.
