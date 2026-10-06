<!-- Refactored from docs/governance/decisions/DECISIONS__part_01.md; source lines 1-142; content preserved. -->
<!-- Part 1/3. Use the family index for navigation. -->
## D-073 — BASE and Palette compose by explicit selection, never hidden color mixing — 2026-09-22

**Decision:** V1.27 treats BASE and Palette as separate authorities. A composition request
selects one semantic role under an explicit mode (`BASE_ONLY`, `PALETTE_ONLY`,
`BASE_THEN_PALETTE`, `PALETTE_THEN_BASE`, or `REJECT_SAME_ROLE`). The result retains both
authorities' provenance and fingerprints when available.

**Reason:** an implicit blend or undocumented precedence rule would create a third semantic
authority and make invalidation/provenance ambiguous. The first appearance-composition layer
must therefore select an existing canonical color rather than inventing a new one.

**Boundary:** no alpha compositing, palette interpolation, lighting, shading, BRDF, reflection,
transmission, style response, gamut mapping, or renderer-specific post-processing is introduced.
Roles without an explicit Palette mapping (`background`, `custom`) fail closed.


## D-074 — Typed appearance role owns the legacy base-color bridge

**Decision:** V1.28 retains `AppearanceResolutionInput.base_color` for compatibility, but when a typed V1.27 composition crosses the boundary the value must be derived from an `AppearanceRoleContribution`. The legacy string is never a second authority. Authored sRGB is preserved exactly; generated values are encoded deterministically from canonical linear-sRGB.

**Reason:** silently maintaining two independent color authorities would permit semantic drift between the typed appearance model and older resolver inputs. The bridge must therefore be explicit, provenance-bearing, geometry-independent and fail closed on contradictory BASE contributions.


## D-075 — Typed appearance input becomes the canonical BASE-domain hand-off

**Decision:** V1.29 promotes `AppearanceRoleContribution` into a canonical `TypedAppearanceInput`.
The BASE domain resolver consumes the typed role directly; the legacy hexadecimal `base_color`
remains only a derived compatibility representation. A typed role automatically contributes an
explicit `appearance_role_bridge` dependency fingerprint to the domain input.

**Reason:** V1.28 proved representation transfer but still left the old input envelope structurally
capable of carrying the color independently. V1.29 closes that authority gap at the domain boundary
without removing the compatibility field prematurely.

**Invariant:** typed role fingerprint, authority component, source ID and lineage must survive into
`DomainResolutionProvenance`. Typed and legacy BASE authorities cannot coexist. Geometry, transform,
renderer state and unrelated siblings remain outside the typed appearance fingerprint.

**Boundary:** no lighting, shading, BRDF, material response, transmission compositing, reflection,
style response, gamut mapping or renderer-specific post-processing is introduced.


## D-076 — Legacy appearance-input builder is compatibility-only

**Decision:** V1.30 treats `build_appearance_input()` and the `AppearanceResolutionInput.base_color`
field as an explicit compatibility boundary. Internal BASE-domain consumers must enter through
`TypedAppearanceInput` and must not reconstruct a legacy BASE contribution merely to call the resolver.
The legacy builder remains available only where the typed-to-legacy bridge is intentional and documented.

**Reason:** V1.29 established the canonical typed authority but the old envelope remained structurally
capable of being consumed directly. Without a source-level migration gate, a future internal caller could
quietly reintroduce the second-authority path and make the architecture appear migrated while still depending
on the legacy representation.

**Invariant:** the V1.30 source audit allows legacy builder usage only in the compatibility definition,
typed-to-legacy bridge and explicit legacy escape hatch. The typed BASE path forwards the role contribution
unchanged and retains the role fingerprint as the domain dependency. Geometry, transforms and unrelated
siblings remain outside appearance identity.

**Boundary:** no COLOR algorithm, lighting, shading, BRDF, material response, transmission compositing,
reflection, style response, gamut mapping or renderer-specific post-processing is introduced.


## D-077 — Typed COLOR consumes the selected role without becoming BASE

**Decision:** V1.31 introduces `TypedColorInput` as a minimal COLOR-domain projection of the
selected `AppearanceRoleContribution`. The COLOR resolver returns the canonical `ColorRGBA`
unchanged and records the role/source/provenance without reconstructing BASE's legacy hexadecimal
field. A typed COLOR role cannot coexist with a second legacy COLOR contribution.

**Reason:** the engine must stop conflating “a color value” with “the BASE domain”. The same upstream
semantic role can legitimately feed more than one domain, but each domain needs an explicit contract
and dependency identity. A minimal projection prevents material, contour, geometry, opacity or
renderer data from becoming accidental COLOR dependencies.

**Invariant:** COLOR identity is derived from target + selected role fingerprint + explicit COLOR
dependencies. Canonical RGB remains linear-sRGB, alpha remains unassociated, and no mixing, grading,
lighting, shading, material response, gamut mapping or compositing occurs.

**Boundary:** V1.31 does not migrate an invented legacy COLOR consumer. The next migration must be
based on an actually existing downstream caller and its semantics must be classified before code is
changed.


## D-078 — COLOR consumer migration requires a proven downstream caller

**Decision:** V1.32 establishes an AST-aware audit boundary before any further COLOR-domain migration. A migration target must be production code outside the COLOR resolver module that actually invokes/consumes the typed COLOR result. Legacy vocabulary, palette authority, color-space conversion infrastructure, and EFFECT-domain color operations are not promoted into COLOR consumers merely because they contain color-related fields.

**Reason:** a text search for `base_color`, `palette`, `pattern`, saturation-like parameters or `ColorRGBA` conversions produces many valid references that belong to other authorities or domains. Treating those references as downstream COLOR consumers would create false positives and could force an inappropriate migration.

**Invariant:** V1.32 records zero downstream production COLOR consumers, zero unclassified findings, and zero unproven dead-code claims. Therefore no runtime COLOR consumer is migrated in this checkpoint.

**Boundary:** no saturation, contrast, vibrance, lightness, temperature, mixing, grading, lighting, shading, material response, gamut mapping or renderer-specific post-processing is added until a real consumer and its input/output color-space semantics are explicitly defined.


## D-079 — Typed COLOR downstream closure is fail-closed — 2026-09-24

**Decision:** V1.33 extends the V1.32 consumer audit with a conservative production call/import graph. The only incoming edge to the typed COLOR resolver is the internal `resolve_color_domain_from_typed()` wrapper; there are zero downstream production callers and zero dynamic resolver escape hatches. Therefore no migration and no COLOR transformation are implemented.

**Reason:** direct text/AST caller searches can miss aliases or dynamic dispatch, while broad color searches can misclassify unrelated authorities. The engine needs evidence that a resolved COLOR value actually crosses the resolver boundary into a production consumer before defining the next operation.

**Invariant:** unresolved dynamic dispatch blocks a PASS instead of being guessed. Public exports are not consumers. Resolver definitions and the internal typed wrapper are not downstream consumers. No runtime semantic version is changed by this audit-only checkpoint.

**Boundary:** no saturation, contrast, vibrance, lightness, temperature, mixing, pattern-to-color conversion, grading, lighting, shading, material response or gamut mapping is introduced until a real downstream caller exists and its color-space/alpha/provenance/dependency/invalidation/visual contract is frozen.


## D-080 — The first real COLOR operation is migrated at its existing effect boundary

V1.33 proved that the typed COLOR resolver has no downstream production caller. The first legitimate color transformation found in the existing runtime is the generic `shadow`/`tint` operation used by `resolve_component`. It is migrated without pretending that it is a typed COLOR resolver caller.

The operation receives canonical linear-sRGB `ColorRGBA`, calculates in explicitly declared encoded sRGB 8-bit space to preserve the established visual law, and returns canonical linear-sRGB RGBA. The base alpha is preserved; `VisualEffect.alpha` is the only effect-strength control. No gamut mapping, lighting, material response or hidden compositing is introduced.


## D-081 — VisualEffect color semantics remain one operation plus scalar effects

**Decision:** V1.35 classifies the complete production `VisualEffect` surface by actual behavior. `shadow` and `tint` both invoke the single canonical `effect.color.srgb8-interpolation` operation; `opacity`, `visibility` and `occlusion` remain scalar visibility/opacity effects. Relation-generated, consequence-generated and legacy-shadow paths are treated as effect creation/provenance paths, not new color algorithms.

**Reason:** V1.34 established the first real color operation. A second transformation must not be inferred from the existence of other effect kinds or color-bearing fields. V1.35 therefore audits the remaining surface and removes only a helper that was proven unreferenced repository-wide.

**Invariant:** no direct encoded-RGB arithmetic exists outside the canonical effect/color-space boundary. Dynamic effect-kind construction is accepted only through existing validated binding paths; unresolved dynamic kinds fail the audit. Shadow/tint remain one operation with one operation identity/version.

**Boundary:** no saturation, contrast, vibrance, lightness, temperature, mixing, pattern-to-color conversion, grading, lighting, shading, material response or gamut mapping is introduced merely to create another COLOR feature.

## D-082 — V1.36 COLOR downstream audit remains fail-closed — 2026-09-24

**Decision:** V1.36 audits every direct production `ColorRGBA` consumer outside the canonical color-space and effect-color modules and does not create a new generic COLOR operation when none is proven. BASE, Palette, persistence, validation and the role bridge remain representation/authority boundaries; the V1.34/V1.35 shadow/tint operation remains the only existing generic color transform; renderer-local RGBA compositing remains renderer-owned; eye-specific color remains isolated.

**Reason:** a color-bearing field, coordinate conversion, palette selection, serialization step or renderer operation is not automatically a generic COLOR transformation. Advancing the runtime by treating one as such would manufacture semantics instead of documenting the actual engine.

**Invariant:** V1.36 proves zero new generic `ColorRGBA` transformations, zero HSL/OKLab/XYZ operations outside the canonical color-space module, zero generic `ColorRGBA` imports in the eye domain, and byte-for-byte unchanged production runtime Python relative to V1.35.

**Boundary:** no saturation, contrast, vibrance, lightness, temperature, mixing, grading, lighting, shading, material response, gamut mapping or renderer color-management algorithm is introduced by this checkpoint. A future real transformation must have its caller, spaces, alpha, bounds, gamut, provenance, lineage, dependencies, invalidation, cache identity, determinism, performance and visual acceptance frozen before implementation.

## D-V1.37 — 2026-09-25 — Do not duplicate an already-certified color transform

The V1.37 audit found one genuine downstream color-modifying consumer, `runtime/effects.py`,
but its transformation is the already-certified `effect.color.srgb8-interpolation` operation
owned by `runtime/effect_color.py`. Because the V1.36 source fingerprint is unchanged,
there is no distinct new transformation to implement. V1.37 therefore remains audit-only.
This is a fail-closed architectural decision: evidence of an existing operation is not treated
as evidence for inventing a second color algorithm.
