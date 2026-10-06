# Impact map

`IMP-FPOR-001`: `production_face_render.py` remains the existing face-overlap call site; Hair/Ear,
Head/Ear, owner geometry and visual-style calls remain separate.

`IMP-FPOR-002`: runtime public export adds the canonical adapter; historical face-overlap visibility
resolver remains public and unchanged.

`IMP-FPOR-003`: no database/persistence files change.

`IMP-FPOR-004`: no COLOR semantic consumer is introduced.

`IMP-FPOR-005`: no cache owner, cache identity or fingerprint algorithm changes.

`IMP-FPOR-006`: visual behavior must remain byte-identical to V1.64 for the five-case production QA.
