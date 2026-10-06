# Impact map — CMP-FACE-HAIR

V1.58 affected the Hair surface depth metadata and the production Hair/Ear interaction consumer.

Affected: `hair.py:46-48`, `production_hair_ear_occlusion.py:1-91`, `production_slice.py:42-44,148-166`, tests, visual QA and benchmark.

Unaffected by design: generic visibility kernel, attribution kernel, Ear geometry, COLOR runtime, database schema, domain-resolution contracts.

Cache/fingerprint: no new cache owner; existing Hair parameter mutation and composite fingerprints remain authoritative.

Determinism: fixed owner ids, fixed depth values and generic-kernel ordering.

Visual impact: YES; real front/+12°/-12° and Hair visible/hidden execution was required.
