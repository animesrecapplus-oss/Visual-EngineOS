<!-- Refactored from ['docs/history/implementation-log/IMPLEMENTATION_LOG__part_01.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_02.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_03.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_04.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_05.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_06.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_07.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_08.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_09.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_10.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_11.md', 'docs/history/implementation-log/IMPLEMENTATION_LOG__part_12.md']; source lines 146-278; content preserved. -->
<!-- Part 2/12. Use the family index for navigation. -->
## Final report / artifact hashes

- V1.27 report SHA-256: `e51ada3fd6261860b03e33ce739b90e21bfa3f8b6f5468c9228b0ad20805efd5`
- V1.27 visual artifact SHA-256: `1627af090d23eca9aa21b914967eea0004609275aa7529f2f366e13d0f1cb9c2`
- V1.27 source/test SHA-256: `3f098696796f256a67ca77c9c9ee49d23e0ade001cf56b6b5b85f7f84dad0fe7`

# V1.28 — Appearance Role Bridge — 2026-09-22

## Objective

Make the transition from the V1.27 typed `AppearanceComposition` model to the
pre-existing `AppearanceResolutionInput.base_color` field explicit and fail-closed.
The legacy field remains available for compatibility, but it is no longer allowed
to behave as an independent authority when a typed role contribution is present.

## What was implemented

1. Added `AppearanceRoleContribution` as a typed renderer-neutral role envelope.
2. Added explicit `BASE` / `PALETTE` source identity.
3. Preserved canonical linear-sRGB `ColorRGBA`.
4. Preserved exact authored sRGB spelling when the selected authority supplied it.
5. Added deterministic canonical-to-legacy encoding for generated colors, without
   claiming that generated values were authored.
6. Copied authority component, source ID, lineage, authority fingerprint and V1.27
   composition fingerprint into the bridge.
7. Added an independently validated bridge fingerprint with no geometry/transform data.
8. Added `bridge_to_appearance_input()` so the old `base_color` string is derived
   from the typed role rather than authored separately.
9. Added explicit rejection when another BASE contribution is supplied alongside
   a typed bridge contribution.
10. Extended `AppearanceResolutionInput` with optional `role_contribution` and a
    contradiction check between the typed bridge and the legacy string.
11. Extended V1.27 composition provenance to retain source IDs and lineage for both
    BASE and Palette authorities; this closes a provenance-loss gap at the bridge.
12. Added mode-aware targeted invalidation so BASE-only and Palette-only requests
    do not depend on the unused authority.
13. Bumped `RESOLUTION_VERSION` from 13 to 14 because the semantic resolution input
    identity now includes a typed role bridge boundary.
14. Added adversarial tests for authored/inherited/generated cases, provenance,
    tampering, conflicting legacy BASE data, geometry independence and mode-scoped
    invalidation.
15. Added a visual QA board with generic object and non-ocular hand samples.

## Self-critique and corrections

### Provenance gap discovered

The first bridge implementation attempted to reconstruct Palette `source_id` and
lineage from the V1.27 composition fields. That would have silently substituted the
authority component ID for the actual source ID. This was rejected as an invalid
provenance shortcut.

Correction: V1.27 `AppearanceCompositionProvenance` now carries:

- `base_source_id`
- `base_lineage`
- `palette_source_id`
- `palette_lineage`

The bridge consumes those values directly.

### Generated representation

Generated colors cannot truthfully receive an authored sRGB representation. The
bridge therefore stores `authored_srgb=None` and only derives the legacy hexadecimal
value through canonical linear-sRGB → sRGB encoding. The visual QA board labels this
case as generated rather than authored.

### Double-authority prevention

The bridge does not merge its typed BASE role with an existing `AppearanceDomain.BASE`
contribution. Such a combination is rejected. This prevents the old dictionary-based
contract from becoming a hidden second source of truth.

### Invalidation scope

The bridge delegates dependency ownership to the existing BASE and Palette resolvers.
The requested composition mode narrows the dependency set. Siblings and geometry do
not become bridge dependencies.

## Visual QA

Generated and manually inspected:

`artifacts/v128_appearance_role_bridge/V1.28_APPEARANCE_ROLE_BRIDGE_SOURCE_TO_LEGACY.png`

The board contains:

- authored BASE object;
- authored Palette object;
- generated BASE hand;
- source swatch;
- bridged display swatch;
- simple geometry proxies;
- source/provenance labels.

The authored source and bridged display swatches visually agree for the diagnostic
8-bit samples. This is evidence of representation preservation, not production
colorimetric certification.

## Verification

Focused V1.28 suite: **18 passed / 0 failed**.

Repository-wide direct run: **777 collected / 776 passed / 1 skipped / 0 failed**.

The only skipped test requires `VISUAL_ENGINE_POSTGRES_DSN`; live PostgreSQL is not
claimed.

Gates:

- A4 PASS
- A5 PASS
- A6 PASS
- A7 OFFLINE PASS
- A8 PASS
- A9 PASS
- A10 PASS

Resolution version: **14**.

## Files created

- `src/visual_engine/runtime/appearance_role_bridge.py`
- `tests/unit/test_v128_appearance_role_bridge.py`
- `tools/visual_qa_v128_appearance_role_bridge.py`
- `tools/verify_v128_appearance_role_bridge.py`
- `docs/domains/color/V1.28_APPEARANCE_ROLE_BRIDGE_CONTRACT.md`
- `artifacts/v128_appearance_role_bridge/V1.28_APPEARANCE_ROLE_BRIDGE_SOURCE_TO_LEGACY.png`
- `artifacts/v128_appearance_role_bridge/V1.28_APPEARANCE_ROLE_BRIDGE_EVIDENCE.json`
- `artifacts/v128_appearance_role_bridge/V1.28_APPEARANCE_ROLE_BRIDGE_MANIFEST.json`
- `artifacts/v128_appearance_role_bridge/V1.28_RELEASE_EVIDENCE.txt`
