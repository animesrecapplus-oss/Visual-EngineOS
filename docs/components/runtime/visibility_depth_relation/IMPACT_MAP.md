# Impact map

Affected: `visibility.py:254-259` and any consumer reading `VisibilityRegionResult.depth_relation`.
Verified consumers: existing production visibility tests and new Head/Ear relation.
No geometry, rendering, COLOR, persistence or cache ownership change.
