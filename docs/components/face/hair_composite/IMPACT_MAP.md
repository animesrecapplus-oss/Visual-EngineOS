# Impact map — CMP-FACE-HAIR-COMPOSITE

Before implementation, V1.56 was read and the remaining Hair child was traced.

Affected: Hair leaf, HumanFace authoring, production registry, Hair composite,
production default, generic SVG Hair role, focused tests, visual QA and benchmark.

Unaffected by design: COLOR runtime, database migrations, domain-resolution contracts,
eye internals, existing Ear/Mouth geometry owners.

Cache/fingerprint: composite cache input includes `stable_digest(hair_geometry)`;
leaf mutation is tested through the existing geometry cache identity.

Determinism: fixed command sequence and explicit registry names.

Visual impact: YES; therefore the full visual execution loop is required.
