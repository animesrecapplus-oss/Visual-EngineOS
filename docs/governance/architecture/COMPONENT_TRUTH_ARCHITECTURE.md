# Component truth architecture — V1.50

## Purpose

This document defines the physical and logical architecture for future component-level engineering without restructuring the whole repository at once.

## Physical ownership

Code follows semantic ownership under `src/visual_engine/components/<parent>/<child>/`.
Documentation follows the same semantic path under `docs/components/<parent>/<child>/`.
For runtime-layer components whose code intentionally remains under `src/visual_engine/runtime/`, the dossier mirrors the semantic runtime path under `docs/components/runtime/<component>/`; this does not imply a physical source move.
Tests may mirror the same semantic path under `tests/components/<parent>/<child>/` as a pilot convention.

## Dossier minimum

Each adopted component has: `INDEX`, `TRUTH`, `ROADMAP`, `CONTRACTS`, `DEPENDENCIES`, `INVARIANTS`, `ADVERSARIAL`, `TEST_STATUS`,
`DECISIONS`, `ERRORS`, `IMPACT`, `EVIDENCE` and `MANIFEST`.

## Adoption rule

Existing components are not mass-migrated. A component enters the new architecture when it is first selected as a pilot or changed by a future brick.
The first pilot is `face/eyes/pupil`.

## Source mapping

The dossier maps every implementation file owned by the component and distinguishes local implementation from compatibility re-exports.

## Interaction mapping

The dossier records parent, child and sibling relations separately from direct imports. A relation may exist without a Python import.

## Truth precedence

Executable code/tests establish observed behaviour. Contracts establish intended guarantees. Decisions explain architectural choices.
Blueprint status is planning metadata until executable evidence confirms it.

## Migration safety

No broad directory move is required for V1.50. Future moves must preserve imports or provide an explicit compatibility facade,
run impact analysis, and prove that the new owner is unique.
