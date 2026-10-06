# Errors and corrections — CMP-RUNTIME-PLACEMENT-CONTRACT

- `ERR-PLAC-001`: first public-facade edit script expected a different import shape in `runtime.__init__`; corrected without changing the intended API.
- `ERR-PLAC-002`: first behavior-identity harness attempted to import the new module from the V1.76 baseline; corrected to compare actual solver output while checking canonical ownership separately.

- `ERR-PLAC-003`: the first regression pass correctly failed because both `artifacts/current/v1.76` and `v1.77` existed; superseded V1.76 evidence was purged and the affected regression batch was rerun successfully.

No unresolved implementation error remains.
