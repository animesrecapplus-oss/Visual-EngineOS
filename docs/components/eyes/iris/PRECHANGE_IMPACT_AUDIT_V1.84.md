# V1.84 — pre-change impact audit

## Baseline

Certified checkpoint: V1.83. Repository archive contains no Git metadata, so Git cleanliness is not claimed from the
checkpoint itself. Runtime source identity is used as the code baseline.

## Reproduced defects

The pre-change IrisSpec constructor accepted `outline_width=NaN`, bool count values and fractional count values.
A numeric string reached an incidental comparison `TypeError`. These are local input-boundary defects.

## Affected surface

Only `src/visual_engine/components/face/eyes/iris/spec.py` is authorized for production-source modification.
The focused Iris test file is the only test addition.

## Consumers

Appearance, styles, generator/cache projection, SVG renderer, paired-eye colour replacement and compatibility
exports were traced before modification. Their valid behaviour is an acceptance invariant.

## Cache/fingerprint

Only `iris_shape` is currently projected into the eye geometry cache input. No V1.84 field is added to that identity.

## Persistence

No IrisSpec persistence adapter or migration was found in the verified source tree. No database change is authorized.

## Visual

Because valid rendering semantics are not intentionally changed, the required visual gate is a before/after
production-render invariance comparison, not a claim of visual improvement.

## Non-goals

No geometry extraction, morphology implementation, pupil relation implementation, COLOR change, renderer refactor,
cache change, persistence change or invented maximum count is permitted.
