# Errors and corrections — CMP-PCOV-001

- `ERR-PCOV-001`: first V1.74 audit tool used a list for Tarjan active-state storage. Corrected before using its graph evidence; final audit passed.
- `ERR-PCOV-002`: first benchmark workload was too large and timed out. Measurement was reduced to a bounded fresh-process sample set; no code optimization was inferred from the timeout.
- `ERR-PCOV-003`: hostile direct-solver test passed NaN rotation to Shapely and exposed a permissive API. Added finite/type validation before geometry operations; test then passed.
- `ERR-PCOV-004`: first visual board displayed only three of four cases. Board layout was corrected to display normal, both boundaries and interaction; visual QA was rerun and passed.

No unresolved implementation error remains at certification. PostgreSQL live verification is not required by this brick because the audit found no placement persistence/schema consumer.
