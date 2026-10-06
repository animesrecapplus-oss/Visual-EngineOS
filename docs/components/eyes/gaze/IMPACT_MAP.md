# Impact map — CMP-EYE-GAZE V1.89

- `IMP-GAZE-001`: owner `gaze/solver.py` changes only `Gaze.__post_init__` plus imports.
- `IMP-GAZE-002`: `GazeSolver` algorithm remains unchanged.
- `IMP-GAZE-003`: `BinocularGazeSolver` remains dependent on shared `_finite`; import must remain.
- `IMP-GAZE-004`: geometry builder and transform consumers receive the same valid authored values.
- `IMP-GAZE-005`: generator cache input contains `Gaze`; valid-value cache identity must remain unchanged.
- `IMP-GAZE-006`: no COLOR consumer, transformation or provenance changes.
- `IMP-GAZE-007`: no database tables, migrations or persistence serialization change.
- `IMP-GAZE-008`: public compatibility exports remain unchanged.
- `IMP-GAZE-009`: deterministic named-direction and target-vector behavior must remain identical for valid inputs.
- `IMP-GAZE-010`: visual output must remain invariant for valid normal/boundary/interaction cases.
- `IMP-GAZE-011`: source line ranges and truth evidence must reference V1.89 only after final implementation.

New fact during implementation: removing `_finite` broke `BinocularGazeSolver`; modification was stopped, impact was
updated, and the import was restored. No shared helper semantics were changed.
- `IMP-GAZE-012`: performance optimization is confined to local validation structure and common built-in numeric fast paths;
  it must not change accepted valid values, rejection classes, solver math or cache identity.
