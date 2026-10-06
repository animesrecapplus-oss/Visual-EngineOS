# CMP-EYE-EYELID — impact map

- `IMP-EYELID-001`: runtime owner `eyelid/spec.py` only.
- `IMP-EYELID-002`: appearance consumer receives the same valid value objects.
- `IMP-EYELID-003`: geometry generation is unchanged for valid inputs.
- `IMP-EYELID-004`: renderer output is unchanged for valid inputs; differential visual evidence required.
- `IMP-EYELID-005`: geometry-cache algorithm and selected eyelid cache fields are unchanged.
- `IMP-EYELID-006`: public exports and serialization surface are unchanged.
- `IMP-EYELID-007`: no database schema, migration or persistence adapter exists for this local value object; no DB change.
- `IMP-EYELID-008`: determinism remains inherited from existing immutable values and deterministic render path.
- `IMP-EYELID-009`: malformed values now fail at construction rather than reaching downstream consumers.

- `IMP-EYELID-010`: hostile testing exposed a numeric overflow exception path; impact analysis was reopened and the
  guard was hardened without changing valid-value behavior.
