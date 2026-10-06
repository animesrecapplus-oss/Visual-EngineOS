# V1.79 — Horizontal micro-component progression policy

## Objective

Advance the project across many visual components without spending an unbounded sequence of versions on one coarse component.

## Rule

At each selection point, choose one micro-component from the verified frontier using:

1. real executable owner;
2. real consumer;
3. clear responsibility boundary;
4. testable invariant/contract;
5. manageable impact;
6. no unresolved higher-priority dependency;
7. no duplicated ownership.

A component that fails these checks remains `PLANNED`, even if it is visually attractive.

## Breadth-first cycle

```text
AUDIT FRONTIER
  ↓
SELECT ONE MATURE MICRO-COMPONENT
  ↓
IMPLEMENT / TEST / CERTIFY
  ↓
UPDATE FRONTIER
  ↓
SELECT A DIFFERENT MATURE MICRO-COMPONENT
  ↓
RETURN LATER TO PREVIOUS COMPONENT WHEN A NEW DEPENDENCY IS NOW REAL
```

The sequence is deterministic at the governance level, while component selection may intentionally rotate across face regions, eyes, ears, hair, mouth and later character domains when evidence permits.

## Hair-specific consequence

Do not add strand density, flyaways or cosmetic strokes before establishing the upstream scalp/cranium boundary and hairline contract. A detail generator without a boundary owner risks encoding a visual patch as anatomy.

## Stop condition

If no candidate has a real consumer and contract, do not invent one. The correct result is `BLOCKED/PLANNED`, not an artificial implementation.

## V1.81 selection evidence

Mouth satisfied the mature-frontier rule through its existing owner, production consumer chain, cache/persistence evidence,
visibility relations and focused tests. The implementation remained within that existing owner and did not create a new child.
