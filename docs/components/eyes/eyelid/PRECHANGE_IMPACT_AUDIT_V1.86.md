# V1.86 — pre-change impact audit

## Baseline

V1.85 certified release is the baseline. Git is not applicable to this project.

## Verified owner

`src/visual_engine/components/face/eyes/eyelid/spec.py:6-47` before modification.

## Consumers

Appearance stores the value; generator projects selected geometry fields into cache inputs; SVG contour/effect
renderers consume widths, colors, flags, styles and opacities; compatibility modules export the value.

## Existing contract evidence

The pre-change source already enforced width/offset/crease-width non-negativity, opacity [0,1] and crease length
(0,1]. Those ranges are preserved.

## Reproduced defects

Before V1.86, `upper_enabled=1`, `upper_enabled="yes"`, `upper_crease_enabled=1`, `upper_width=NaN`,
`upper_width=inf`, `upper_crease_offset=NaN`, `upper_crease_offset=inf` and `upper_crease_width=NaN` were accepted.

Some other non-finite fields were rejected incidentally by range comparisons. The defect is therefore inconsistent
numeric/type validation, not absence of all validation.

## Scope / risk

Only local construction validation is changed. No geometry formula, renderer algorithm, cache identity, visibility,
COLOR, database or public export is modified.

## Stop conditions

If a consumer requires a previously accepted malformed value, or if valid-render differential tests change, stop and
re-open this impact analysis before continuing.
