# Component truth

Identity: `CMP-RUNTIME-PRODUCTION-PAIR-OCCLUSION`.

Parent: production spatial runtime.
Children: none.
Owner: `src/visual_engine/runtime/production_pair_occlusion.py:17-107`.

Responsibility: validate one real owner pair, materialize exactly one semantic area region per owner,
construct one `Occluder`, and delegate visibility plus optional attribution to the authoritative generic kernels.

Non-responsibility: anatomy, geometry generation, renderer paint policy, COLOR, persistence schema, cache lifetime,
or domain-specific owner-kind rules.
