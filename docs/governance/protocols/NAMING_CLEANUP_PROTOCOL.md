# Naming, repetition and cleanup protocol — V1.50

## Naming

Names encode semantic ownership, not implementation chronology. Use stable component names and explicit responsibility names.
Do not create `final`, `new`, `temp`, `misc`, `utils2`, `fix`, `old`, `backup`, `test2` or date-suffixed production files.

## IDs

Use stable IDs with a category prefix: `CMP`, `FILE`, `CON`, `INV`, `TST`, `ADV`, `REL`, `DEC`, `ERR`, `IMP`, `EVD`.
IDs must be unique within the project registry and must not be silently reused after deletion.

## Duplication

Audit four classes: exact code duplication, structural duplication, semantic duplication and intentional equivalence.
Only the first three become refactor candidates. Similarity alone never proves duplicate responsibility.

## File budget

Production code and durable text are capped at 150 lines unless an explicit governance exception exists.
The threshold is a decomposition trigger, not a reason to split unrelated lines into artificial fragments. Existing oversized modules are tracked in `LINE_BUDGET_DEBT.md` and are frozen against unrelated feature growth until a controlled extraction certifies them.

## Cleanup

Before certification remove temporary scripts, caches, stale generated files, obsolete release copies, pycache/pyc and
superseded current evidence. Keep `artifacts/` itself and retain only the current brick's evidence.

## Historical truth

Do not delete durable history merely to keep the tree small. Move decisions, defects, corrections and line maps into
bounded history documents. Generated output and durable engineering knowledge have different retention rules.
