# Impact map — CMP-FACE-EAR

- `IMP-FE-001`: source — `ear.py:15-27,30-61` gains strict numeric/finite validation for malformed parameter state.
- `IMP-FE-002`: authoring — `entities/face.py:35-42` remains unchanged.
- `IMP-FE-003`: production registry/composite remain unchanged.
- `IMP-FE-004`: renderer — valid geometry contract and semantic `ear` role remain unchanged.
- `IMP-FE-005`: cache/fingerprint — invalid values now fail before cacheable geometry exists; valid cache identity remains unchanged.
- `IMP-FE-006`: persistence — no schema or serializer change.
- `IMP-FE-007`: COLOR — no semantic consumer introduced; COLOR remains frozen.
- `IMP-FE-008`: siblings/parent — Eye, Nose, Mouth and Hair geometry/relations are not modified.
- `IMP-FE-009`: visual behavior — valid production renders must remain byte-identical to V1.79; only previously malformed inputs change from undefined/unsafe coercion to rejection.
