# Impact analysis protocol — V1.50

## Trigger

Impact analysis is mandatory before modifying a source file, contract, test fixture, schema, database mapping,
renderer boundary, documentation contract or generated-evidence producer.

## Required questions

1. What exact file/line/function changes?
2. Which component owns it?
3. Which parent, children and siblings can observe the change?
4. Which production consumers import or call it?
5. Which dependencies can be affected?
6. Which public or internal contracts change?
7. Which invariants become newly exposed or invalid?
8. Which unit, adversarial, integration and visual tests must run?
9. Which cache/fingerprint/provenance identities can change?
10. Can persistence/database records become incompatible?
11. Can determinism change?
12. Can rendering, frame composition or video output change?
13. What old behaviour must remain identical?
14. What evidence will prove the answer?

## Impact classes

`DIRECT` — changed owner or direct caller.

`RELATIONAL` — parent, child or sibling sharing a contract.

`TRANSVERSE` — geometry, transform, visibility, appearance, cache, persistence or renderer boundary.

`VISUAL` — any change capable of altering SVG, raster, frame ordering or video composition.

## Test selection

Every impacted contract gets its direct tests. Every relational impact gets interaction tests. Every transverse impact
gets the corresponding subsystem regression. Every visual impact gets deterministic before/after evidence and human
inspection. Unaffected suites may be skipped only with a documented reason and evidence.

## Change record

The impact record must list affected files, contracts, tests, risks, expected unchanged behaviour and evidence paths.
No implementation starts until the impact record is internally coherent.

## Re-open rule

If implementation reveals a new consumer, dependency, invariant or visual effect, stop and update the impact analysis.
Do not silently continue under the old scope.
