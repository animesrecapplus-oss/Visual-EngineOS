<!-- Refactored from docs/governance/roadmap/ROADMAP__part_01.md; source lines 526-649; content preserved. -->
<!-- Part 5/16. Use the family index for navigation. -->
### Boundary

No state, geometry, appearance or effect mutation is performed here. The next
integration gate is to audit/reuse the existing state/effect precedence systems
rather than creating a second mutation policy engine.

## V1.3 — Consequence → State/Effect Binding Boundary — 2026-09-15

Implemented `runtime/consequence_bindings.py` as the one-way bridge from aggregated
`ResolvedConsequence` objects to the existing `StateActivation` and `VisualEffect`
contracts.

### Implemented

- explicit consequence-to-state bindings;
- explicit consequence-to-effect bindings;
- reuse of existing state precedence and effect composition engines;
- stable effect IDs derived from request fingerprints;
- loss-aware `unbound` output for missing mappings;
- explicit non-interpretation of geometry/appearance requests;
- regression tests for precedence ownership and fail-closed behavior.

### Boundary

No component mutation is performed. The binding compiler only translates accepted
semantic consequences into existing downstream envelopes.

### Next gate

Define the generic application/resolution transaction that attaches those envelopes
to a target resolution context while preserving provenance, region granularity,
dependency fingerprints and deterministic invalidation. Appearance/color remains
downstream.

## V1.3 checkpoint — Consequence resolution bridge

The accepted consequence path is now connected to the existing immutable `ResolutionContext`. Consequence-derived `StateActivation` candidates are resolved by the existing state policy, while `VisualEffect` objects are consumed by the existing effect policy. Geometry and appearance consequences remain intentionally unbound until their dedicated contracts exist. Resolution fingerprint semantics include consequence-derived state activations, and the resolution version is now `8`.

## V1.3 — Appearance Resolution Contract — 2026-09-15

Defined the renderer-neutral appearance boundary without starting color/lighting
implementation prematurely.

Implemented `runtime/appearance_contract.py` with explicit appearance domains,
immutable input/output envelopes, typed contributions, deterministic state
canonicalization, and fail-closed unresolved-domain reporting.

The contract preserves the separation between base color, material, lighting,
transmission, reflection and emission. It does not interpret semantic payloads or
perform shading. This is the prerequisite boundary for the future Color
Intelligence Engine.

## V1.3 checkpoint — Appearance Layer Resolution

`Component.appearance` now has an explicit resolver boundary into the appearance
contract. Local layers require explicit domain bindings; no implicit ancestor
inheritance is introduced. Declaration order and conflict priority are separate;
active-state activation is explicit; target-applicable `VisualEffect` objects become
typed EFFECT contributions; duplicates/conflicts fail closed; provenance and a stable
layer-resolution dependency digest are retained. The digest enters
`AppearanceResolutionInput` without replacing the global resolution fingerprint.

The next gate is to audit the **semantic payload contract** of each appearance domain
before implementing color/material/lighting behavior. No domain-specific shading is
claimed by this checkpoint.


## V1.3 — Appearance Domain Contract Validation

Implemented the semantic validation gate between `AppearanceContribution` and future
domain algorithms. The seven rendering domains now have explicit closed vocabularies,
value kinds and numeric boundaries. Unknown keys fail closed; required fields and
range constraints are explicit; validation performs no normalization or rendering.
`STATE` and `EFFECT` remain owned by their existing contracts.

Next gate: implement the first domain algorithm only after its validated payload
contract is stable.

## V1.3 — Domain Resolver Input/Result Contract — 2026-09-15

Implemented the resolver transaction boundary after semantic domain validation.
`DomainResolutionInput` isolates one rendering domain and carries explicit target,
validated contributions, active states, named dependency digests, resolver identity
and contract version. `DomainResolutionResult` provides explicit lifecycle status,
validated domain fields, unresolved reasons, provenance and dependency identity.

The result vocabulary is tied back to the existing `DomainContract`, preventing a
future resolver from silently inventing output fields. Input and output identities
are content-addressed for deterministic caching/invalidation. Successful and partial
results require provenance; stale/mismatched inputs fail closed.

`STATE` and `EFFECT` remain outside this rendering-domain resolver boundary because
their existing policy engines own those semantics.

**Verification:** 318 tests PASS; compileall PASS.

**Next gate:** define the individual domain-resolution semantic contracts/algorithms,
starting with the domain whose prerequisites can be stated completely without
introducing hidden cross-domain behavior.


## V1.3 — BASE Domain Resolution — 2026-09-15

**Status: implemented and verified.** The first concrete appearance-domain algorithm
now resolves a single authoritative opaque BASE contribution into the existing generic
`DomainResolutionResult`. Multiple contributions and translucent BASE authority are
rejected because no precedence or underlay semantics exist yet. RGBA alpha remains
untouched data.

Next domain work must introduce explicit semantics before enabling composition or
cross-domain interaction; no hidden precedence is permitted.

## V1.3 — MATERIAL Domain Resolution — 2026-09-15

Status: **implemented and verified**.

The MATERIAL domain now has a concrete authoritative-record resolver. One
non-empty opaque contribution resolves; zero, multiple or translucent authority
is rejected without implicit precedence or composition. Valid fields are preserved
without physical or artistic transformation.

Next: define the next domain algorithm only after its composition semantics and
dependencies can be stated without hidden cross-domain behavior.
