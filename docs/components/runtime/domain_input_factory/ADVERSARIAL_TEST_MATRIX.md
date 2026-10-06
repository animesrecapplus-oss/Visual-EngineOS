# Adversarial matrix — CMP-DOMAIN-INPUT-FACTORY

| ID | Attack | Expected | Evidence |
|---|---|---|---|
| ADV-DIF-001 | invalid dependency object | reject before `.name` access | TST-DIF-001 |
| ADV-DIF-002 | duplicate dependency names | canonical contract rejects | TST-DIF-002 |
| ADV-DIF-003 | unsorted dependency tuple | canonicalize | TST-DIF-003 |
| ADV-DIF-004 | empty/invalid digest | canonical contract rejects | TST-DIF-004 |
| ADV-DIF-005 | typed-role conflicting dependency | reject | TST-DIF-005 |
| ADV-DIF-006 | wrong domain | reject | TST-DIF-006 |
| ADV-DIF-007 | facade reverse import | forbidden | TST-DIF-007 |
| ADV-DIF-008 | duplicate implementation | audit must return zero | TST-DIF-008 |
| ADV-DIF-009 | new SCC | audit must preserve baseline SCC set | TST-DIF-009 |
| ADV-DIF-010 | persistence consumer | audit must return false | TST-DIF-010 |

`DECLARED` or `BLOCKED` is never converted to PASS.
