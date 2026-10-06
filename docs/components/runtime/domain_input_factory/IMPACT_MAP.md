# Impact map — CMP-DOMAIN-INPUT-FACTORY

## IMP-DIF-001 — source

Created `runtime/domain_input_factory.py` lines 1–64; reduced `domain_resolution.py` to compatibility/result responsibility; rewired direct production consumers.

## IMP-DIF-002 — consumers

BASE `176,207`, COLOR `22`, MATERIAL `138` now use the canonical owner. Historical facade remains available.

## IMP-DIF-003 — contracts/invariants

Preserve domain admission, state/dependency canonicalization, typed-role dependency identity, field values and input digest semantics for valid inputs.

## IMP-DIF-004 — cache/fingerprint/provenance

No cache implementation changes. Input digest remains owned by `DomainResolutionInput`; no new fingerprint is created.

## IMP-DIF-005 — persistence/database

Repository audit found zero direct DB consumers and zero migrations. No persistence change is justified.

## IMP-DIF-006 — visual

No geometry/render code is touched. Existing production render tests verify unchanged downstream behavior. New visual evidence would be fabricated.

## IMP-DIF-007 — determinism/performance

Fresh-process benchmark compares the V1.53 factory path with V1.54 canonical ownership. No optimization is introduced.
