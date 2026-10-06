# Error register — CMP-DOMAIN-INPUT-FACTORY

## ERR-DIF-001 — permissive dependency sequence

The pre-extraction factory could access `.name` on arbitrary sequence members. V1.54 rejects non-`DomainDependency` items before sorting.

## ERR-DIF-002 — compatibility ownership ambiguity

The factory implementation lived in `domain_resolution`, making ownership indistinguishable from the generic facade. V1.54 gives the construction policy a canonical owner while retaining compatibility imports.

## Open errors

None identified in the selected responsibility after focused hostile testing.

Live PostgreSQL remains an environmental verification boundary and is not represented as a component error.
