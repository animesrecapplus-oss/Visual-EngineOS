# Invariants and assumptions

`INV-RC-001`: construction is deterministic for identical input values.

`INV-RC-002`: canonicalization never delegates state precedence or effect composition to this owner.

`INV-RC-003`: effect IDs are unique inside one context.

`INV-RC-004`: target-scoped filtering never admits an effect targeted at another component.

`INV-RC-005`: legacy shadow remains a compatibility input and is materialized only when `shadow_alpha` is non-zero.

`INV-RC-006`: fingerprint ownership stays in `runtime.versioning`; cache identity semantics are not reimplemented.

`INV-RC-007`: extracting this contract must not change resolution inputs, SVG output, visibility, or cache statistics.

Assumption: existing `VisualEffect` and `StateActivation` contracts remain the semantic owners of their respective fields.
