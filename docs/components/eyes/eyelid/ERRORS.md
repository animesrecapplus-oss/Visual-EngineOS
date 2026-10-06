# CMP-EYE-EYELID — errors

- `ERR-EYELID-001`: pre-V1.86 boolean fields accepted integer/string truthy values.
- `ERR-EYELID-002`: pre-V1.86 width/offset/crease-width fields could accept NaN or infinity because relational checks
  alone do not reject non-finite values.
- `ERR-EYELID-003`: pre-V1.86 numeric fields did not enforce a common non-coercive numeric boundary.

Resolution: V1.86 adds local bool/type/finiteness guards before the existing range checks. During hostile review, very large integers were found to make `math.isfinite` leak `OverflowError`; the guard was revised to convert that overflow into the contract-level `ValueError`.

No unresolved V1.86 implementation error is recorded.
