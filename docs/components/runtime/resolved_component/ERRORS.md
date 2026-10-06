# Errors

`ERR-RCMP-001`: a compatibility import accidentally becoming a second class owner would break identity; guarded by
canonical-owner and compatibility tests.

`ERR-RCMP-002`: adding mutable fields or dynamic attributes would break cache-safe immutable-result semantics; guarded
by frozen/slot tests.

`ERR-RCMP-003`: result-envelope extraction changing resolver output would be a silent regression; guarded by production
five-case identity and full regression.
