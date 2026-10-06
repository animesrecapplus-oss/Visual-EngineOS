# CMP-EYE-LASH — decisions

## DEC-LASH-001 — select lash local boundary

**Options:** defer to another face component; modify eyelid; harden lash spec.

**Evidence:** lash has an executable owner and real consumers; malformed counts can reach `range()`; several float
fields accept non-finite values before V1.85.

**Trade-off:** a narrow validation change is lower risk than touching renderer/geometry behavior.

**Decision:** harden `lashes/spec.py` only.

## DEC-LASH-002 — strict numeric typing without coercion

**Decision:** use `Integral`/`Real` plus explicit bool rejection and `math.isfinite`; do not coerce strings/fractions.

**Reason:** preserves authored type semantics and matches the V1.82/V1.84 hardening pattern without widening scope.

## DEC-LASH-003 — no maximum count

No verified resource ceiling or contract supports a new maximum. Therefore none is invented.
