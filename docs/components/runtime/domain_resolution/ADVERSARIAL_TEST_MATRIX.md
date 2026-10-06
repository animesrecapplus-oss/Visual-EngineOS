# Domain-resolution hostile matrix — V1.53

| ID | Attack | Status | Protection |
|---|---|---|---|
| ADV-DOMAIN-015 | non-string target ID | PASS | input constructor type guard |
| ADV-DOMAIN-016 | non-`AppearanceDomain` domain | PASS | explicit runtime type guard |
| ADV-DOMAIN-017 | invalid contribution container/item | PASS | typed contribution guard |
| ADV-DOMAIN-018 | duplicate contribution IDs | PASS | uniqueness invariant |
| ADV-DOMAIN-019 | cross-domain contribution | PASS | domain membership guard |
| ADV-DOMAIN-020 | non-canonical active states | PASS | canonical tuple guard |
| ADV-DOMAIN-021 | invalid dependency container/item | PASS | typed dependency guard |
| ADV-DOMAIN-022 | duplicate/unsorted dependency names | PASS | ordering/uniqueness guards |
| ADV-DOMAIN-023 | invalid dependency digest | PASS | canonical SHA-256 guard |
| ADV-DOMAIN-024 | role target/domain conflict | PASS | role boundary guards |
| ADV-DOMAIN-025 | role + legacy authority collision | PASS | contradiction rejection |
| ADV-DOMAIN-026 | legacy facade import cycle | PASS | owner dependency-direction test |
| ADV-DOMAIN-027 | persistence coupling | PASS | repository consumer audit |
| ADV-DOMAIN-028 | duplicate implementation | PASS | AST exact-duplicate audit |

`DECLARED` and `BLOCKED` are never interpreted as PASS.
