# Impact map — CMP-FACE-VIS-001

- `IMP-FVIS-001`: `entities/face.py` default anchors/parameters change visible face proportions.
- `IMP-FVIS-002`: `face/hair.py` geometry topology and generator version change; cache identity must change.
- `IMP-FVIS-003`: `face/generators.py` nose geometry changes visible bridge/tip placement.
- `IMP-FVIS-004`: production hair/ear optical relation must remain valid.
- `IMP-FVIS-005`: eye geometry is expected unchanged and is compared explicitly.
- `IMP-FVIS-006`: no persistence/schema change.
- `IMP-FVIS-007`: no COLOR algorithm change; only existing authored visual colors are sampled.
- `IMP-FVIS-008`: deterministic SVG and component-level comparisons are required.
