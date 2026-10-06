# Evidence — CMP-FACE-VIS-001

- `EVD-FVIS-001`: multi-variant production board covering ears, eyes, hair, nose/mouth, color, face shape and eye detail.
- `EVD-FVIS-002`: targeted calibration suite passes.
- `EVD-FVIS-003`: existing hair/ear relation suite passes after side-lock correction.
- `EVD-FVIS-004`: production normal/±30°/zoom interaction renders generated after correction.
- `EVD-FVIS-005`: unrelated eye/head component hashes remain identical to V1.77.
- `EVD-FVIS-006`: final regression collection is 1164 tests; 1163 passed and one PostgreSQL test is skipped because `VISUAL_ENGINE_POSTGRES_DSN` is absent.
- `EVD-FVIS-007`: final fresh-process production render benchmark median is 68,673,361.5 ns versus V1.77 baseline 65,516,842.0 ns, +4.818%; measurement only.
- `EVD-FVIS-008`: compileall passed immediately before final purge.
