# Hostile review protocol — V1.50

## Objective

The hostile phase attempts to falsify the implementation instead of confirming nominal examples.

## Mandatory attack families

- impossible states;
- wrong or mixed types;
- `NaN`, `+∞`, `-∞`;
- zero denominators and empty collections;
- negative, zero, maximal and near-limit values;
- overflow/underflow and precision loss;
- malformed colors, paths, transforms or identifiers;
- contradictory inputs;
- circular dependencies;
- order-dependent execution;
- nondeterminism and unstable hashes;
- cache stale/fresh confusion;
- parent/child contract conflicts;
- sibling interaction conflicts;
- occlusion and visibility edge cases;
- API over-permissiveness;
- catastrophic complexity/performance;
- compatibility regressions;
- silent visual regressions.

## Required result

Every attack is classified as `PASS`, `FAIL`, `NOT_APPLICABLE` or `BLOCKED`.
`BLOCKED` requires a reason and cannot silently count as pass.

## Reviewer questions

The Reviewer independently asks: can this API admit an impossible state? Can a consumer misuse it without an error?
Can a future child violate a parent assumption? Can a renderer duplicate semantic logic? Can a cache return stale output?
Can two valid components become invalid when composed? Can a future refactor break provenance or determinism?

## Adversarial evidence

A hostile test must identify the input, expected invariant/failure, observed result and regression protection.
A successful hostile test does not prove completeness; the attack matrix itself is part of the durable component truth.
