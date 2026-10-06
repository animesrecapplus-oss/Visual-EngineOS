# Invariants and assumptions

`INV-HEO2-001`: Head/Ear overlap is geometric and deterministic under the production camera transform.
`INV-HEO2-002`: equal authored depth remains semantically `COPLANAR`; the explicit relation flag supplies the occlusion policy.
`INV-HEO2-003`: hidden Head preserves geometric coverage but produces no optical loss.
`INV-HEO2-004`: parent visual mutation invalidates/re-resolves the production style used by the relation.

Assumption: current HumanFace head surface is the foreground painter relative to Ear at equal depth.
