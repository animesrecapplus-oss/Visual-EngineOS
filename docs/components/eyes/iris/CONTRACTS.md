# Iris contracts — V1.84

`CON-IRIS-001` — `ring_count` and `pattern_count` are integer values; bool is rejected. `ring_count >= 0` and
`pattern_count >= 1`.

`CON-IRIS-002` — `glow`, `opacity`, `pattern_strength` and `outline_width` are Real, non-bool and finite.

`CON-IRIS-003` — `glow` and `opacity` are bounded to `[0,1]`; `pattern_strength` is bounded to `[0,1]`;
`outline_width >= 0`.

`CON-IRIS-004` — authored iris, outline, inner and outer colours continue to use the shared eye colour validator.

`CON-IRIS-005` — `IrisSpec` remains an immutable frozen value object.

No V1.84 contract is promoted for `shape`, `pattern` vocabulary, pupil containment, gaze, eyelid exposure,
cornea attachment, highlights, cache lifetime or database representation. Those boundaries require separate evidence.
