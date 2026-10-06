# Errors

`ERR-PRS-001`: V1.71 re-audited `resolve_component_contract` first; the same compatibility graph creates a new `runtime.contract ↔ runtime.resolve_component_contract` cycle if extracted with a static facade dependency. The candidate remains rejected; no dynamic import or duplicate resolver was introduced.

`ERR-PRS-002`: first focused hostile test mutated the authoring tree with a third `Ear`, which correctly caused the existing face generator invariant to reject the render. The test was corrected to use an unrelated `Decor` child; no production code change was needed.

No declared or blocked item is promoted to PASS.
