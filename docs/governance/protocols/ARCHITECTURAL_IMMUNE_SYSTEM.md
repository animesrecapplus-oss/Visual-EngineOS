# Architectural immune system — V1.50

## Purpose

This protocol turns architecture, contracts, tests, evidence and impact analysis into one mandatory control system.
It applies to every future implementation brick; V1.50 establishes it and pilots it on `face/eyes/pupil`.

## Non-negotiable principles

1. One semantic responsibility has one canonical owner.
2. A component is not only code: it includes contracts, invariants, tests, decisions, errors and evidence.
3. A relation between components is a first-class engineering concern.
4. No modification is considered local until impact is analysed.
5. A passing unit test does not close visual behaviour when rendering can change.
6. A visual sample without reproducible inputs is not regression evidence.
7. A declared feature is not implemented until executable evidence exists.
8. A parent status never promotes an unverified child.
9. Generated evidence is disposable; durable knowledge belongs in bounded documentation.
10. `artifacts/` remains present and retains only the current brick evidence.
11. No extraction is justified only by the line-count threshold.
12. COLOR remains frozen unless a real downstream consumer demonstrates a missing contract.

## Mandatory lifecycle

`VERIFY → ARCHITECT → IMPACT → IMPLEMENT → HOSTILE TEST → REVIEW → OPTIMIZE → INTEGRATE → VISUALIZE → DOCUMENT → PURGE → CERTIFY`

A stage may reopen an earlier stage. Acceptance is forbidden when a required stage is unresolved.

## Roles

**Architecte:** responsibility, owner, boundaries, contracts, dependencies and impact.

**Implémenteur:** only the approved change; no opportunistic refactor.

**Testeur hostile:** attempts to break invariants, types, bounds, determinism and interactions.

**Reviewer:** searches architectural weaknesses, hidden coupling, impossible states and silent regressions.

**Optimiseur:** measures first; changes only demonstrated cost centres; re-runs regression.

**Intégrateur:** validates parent/child/sibling/system interactions and public compatibility.

## Stop conditions

Stop immediately when ownership is ambiguous, a contract is contradictory, a required consumer is unknown,
a cycle is introduced, an invariant has no test, visual behaviour changed without evidence, or generated evidence
cannot be reproduced. Resolve the ambiguity before implementation continues.
