# Traceability ID protocol — V1.50

## ID families

`CMP-*` component; `FILE-*` implementation file; `CON-*` contract; `INV-*` invariant; `TST-*` deterministic test;
`ADV-*` hostile test; `REL-*` component relation; `DEC-*` decision; `ERR-*` defect; `IMP-*` impact record; `EVD-*` evidence.

## Directionality

Every important contract must be traceable forward to implementation/tests/evidence and backward to its consumers,
source decisions and input provenance where applicable.

## Minimum chain

`DEC → CON → INV → CODE → TST/ADV → EVD`

For runtime behaviour:

`PROMPT/INPUT → PARAMETER → COMPONENT → GEOMETRY → TRANSFORM → VISIBILITY/APPEARANCE → RENDER → EVD`

The reverse path must be possible for diagnosed defects.

## Relations

A relation ID names both endpoints and the contract crossing the boundary. Relations are not inferred only from folder layout.

## Line mapping

Each implementation change records exact final line ranges after source freeze. Line numbers are evidence metadata and are
not used as semantic identifiers; stable IDs are.

## Status integrity

A traceability record may point to a future task, but must label it `PLANNED` or `DECLARED`. It must never use an implementation
status merely because a blueprint entry exists.
