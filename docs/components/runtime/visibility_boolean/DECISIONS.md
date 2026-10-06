# Decisions — CMP-VBOOL-001

- `DEC-VBOOL-001`: select boolean planar composition because it is a distinct contract/responsibility inside `runtime.visibility`.
- `DEC-VBOOL-002`: make `runtime.visibility_boolean` the canonical owner and preserve historical imports from `runtime.visibility`.
- `DEC-VBOOL-003`: after a +11.941% benchmark regression in the first implementation, do not route the hot visibility loop through new Python helpers.
- `DEC-VBOOL-004`: keep cache/fingerprint/provenance, persistence/database, COLOR and renderer semantics frozen.
- `DEC-VBOOL-005`: benchmark the final implementation against the certified V1.74 checkpoint before certification.
