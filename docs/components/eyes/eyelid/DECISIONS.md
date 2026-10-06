# CMP-EYE-EYELID — decisions

## DEC-EYELID-001 — local hardening only

Options: modify the existing owner; create a validation façade; refactor shared validation first.

Evidence: one existing owner already performs all eyelid validation and has direct consumers.

Decision: modify only `eyelid/spec.py`. A façade or shared refactor would enlarge the surface without a verified need.

## DEC-EYELID-002 — preserve existing numeric ranges

Evidence: current comparisons are the only verified local numeric range contract.

Decision: add type/finiteness guards before the existing comparisons; do not invent new maxima or anatomical ratios.

## DEC-EYELID-003 — no style-vocabulary expansion

The `ContourStyle` vocabulary already exists. V1.86 does not change or duplicate that contract.

## DEC-EYELID-004 — overflow must not escape the input contract

Hostile testing showed that `math.isfinite` can raise `OverflowError` for extremely large integer/fraction values.
The implementation catches that numeric overflow and rejects the value as malformed instead of leaking an internal error.
