# Component truth protocol — V1.50

## Required identity

Every real component or subcomponent has a stable identifier and a semantic path.
Example: `CMP-EYE-PUPIL` → `face/eyes/pupil`.

## Required truth fields

Each component dossier must state:

- identity and parent;
- children and sibling relations;
- exact responsibility and explicit non-responsibility;
- real consumers and why they consume it;
- guarantees and public contracts;
- dependencies and ownership of those dependencies;
- assumptions and their validation status;
- invariants and failure behaviour;
- tests protecting each important invariant;
- changes likely to break the component;
- decisions and rationale;
- known errors and correction history;
- current implementation status;
- evidence required for acceptance.

## Status vocabulary

`PLANNED` = intended but not implemented.

`DECLARED` = documented or typed, but executable evidence is incomplete.

`IMPLEMENTED` = executable behaviour exists and its direct contract tests pass.

`INTEGRATED` = parent/child/system interaction tests pass.

`VISUALLY_VALIDATED` = required visual evidence was inspected and accepted.

`CERTIFIED` = all applicable gates pass and documentation/evidence are frozen.

A component can never skip from `PLANNED` to `CERTIFIED`.

## Parent/child rule

A parent may consume a child only through the child's declared contract. The parent must not duplicate the child's
rules. A child may depend on a parent contract only where the dependency is explicit and acyclic.

## Relation rule

Every non-trivial interaction receives a relation record: source, target, direction, contract, invariant,
known failure mode and tests. This prevents correctness from being inferred from isolated component tests.

## File truth

Every implementation file in a pilot dossier receives a file record containing responsibility, owner, consumers,
dependencies, invariants, tests, impact surface and line count. New/modified code requires explanatory comments on
non-trivial logic; the pilot additionally enforces a comment-coverage gate on every non-blank code line.
