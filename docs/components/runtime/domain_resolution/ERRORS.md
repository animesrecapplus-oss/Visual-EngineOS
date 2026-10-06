# Domain-resolution error register — V1.53

## ERR-DOMAIN-004 — permissive input domain type

The pre-V1.53 `DomainResolutionInput` delegated domain admission to a membership guard that did not reject every
non-enum value at the constructor boundary. V1.53 adds an explicit `AppearanceDomain` runtime type check.

## ERR-DOMAIN-005 — permissive dependency item type

The previous constructor assumed dependency entries exposed `.name` and `.digest`. V1.53 rejects non-`DomainDependency`
items before ordering access, closing an API-boundary type hole.

## Open errors

None identified in the selected input responsibility after focused hostile tests. Live PostgreSQL remains an expected
environmental skip when its DSN is absent; it is not converted into PASS.
