# Component truth — CMP-DOMAIN-INPUT-FACTORY

## Identity

`CMP-DOMAIN-INPUT-FACTORY` is the canonical construction policy for immutable domain-resolution inputs.

## Responsibility

Lines 21–64 of `domain_input_factory.py` validate the construction boundary, canonicalize dependency/state ordering, inject typed-role dependency identity, and construct the canonical `DomainResolutionInput` value object.

## Non-responsibility

It does not own value-object storage semantics, result status, result validation, domain algorithms, persistence, cache/fingerprint lifecycle, geometry, visibility or rendering.

## Ownership

`runtime.domain_input_factory` is the sole factory implementation owner. `runtime.domain_resolution:42` is only the compatibility re-export. `runtime.__init__:151` exposes the canonical public symbol.

## Relations

Parent: runtime resolution layer. Siblings: input contract, result contract, result validation, BASE/COLOR/MATERIAL resolvers. No child component is owned by this factory.

## Guarantees

Valid historical inputs produce equivalent canonical values and deterministic input digests. Invalid dependency item types are rejected before ordering access.

## IDs

`CMP-DOMAIN-INPUT-FACTORY`; `FILE-DIF-001..006`; `REL-DIF-001..004`.
