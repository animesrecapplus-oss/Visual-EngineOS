# CMP-EYE-LASH — impact map

## IMP-LASH-001 — source

Only `components/face/eyes/lashes/spec.py` is authorized for runtime modification.

## IMP-LASH-002 — consumers

Appearance, styles/profiles, upper/lower render helpers and compatibility exports must continue accepting all valid
existing defaults and authored presets.

## IMP-LASH-003 — geometry/rendering

No geometry algorithm, lash placement formula, terminal exclusion, visibility rule or SVG emission algorithm changes.

## IMP-LASH-004 — cache/fingerprint

No cache input or fingerprint implementation is modified; validation occurs at value construction only.

## IMP-LASH-005 — persistence

No migration, schema or database adapter is changed; no verified direct persistence owner exists for LashSpec.

## IMP-LASH-006 — determinism

No random source, seed, ordering or renderer iteration algorithm changes.

## IMP-LASH-007 — visual behavior

Valid inputs must render identically to V1.84. Invalid inputs must fail earlier and explicitly.
