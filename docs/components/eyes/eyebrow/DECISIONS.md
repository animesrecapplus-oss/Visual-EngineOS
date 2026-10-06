# V1.87 — decisions — CMP-EYE-EYEBROW

## DEC-EYEBROW-001 — select eyebrow horizontally

Options: continue eyelid/lash/iris/pupil hardening; promote planned anatomy; select another executable boundary.
Evidence: V1.86/V1.85/V1.84/V1.82 already hardened those recent owners; `BrowSpec` has real consumers and a
reproducible local validation defect. Decision: select `CMP-EYE-EYEBROW`.

## DEC-EYEBROW-002 — keep scope local

Only `eyebrow/spec.py` changes at runtime. No shared validation helper is modified because that would expand the
impact surface to unrelated components.

## DEC-EYEBROW-003 — reject float-conversion overflow

Existing `math.isfinite` on a huge integer can raise `OverflowError`. The local contract therefore treats numeric values
that cannot be safely tested as finite as invalid rather than leaking an implementation exception.

## DEC-EYEBROW-004 — preserve placement authority

`min_eye_gap`/`max_eye_gap` ranges remain unchanged. No new anatomical proportion, maximum, geometry or placement rule
is invented.
