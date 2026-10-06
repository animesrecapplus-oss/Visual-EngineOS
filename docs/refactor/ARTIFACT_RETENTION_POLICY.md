# Generated-artifact retention policy — corrected at V1.49

## Rule

`artifacts/` is part of the project and must remain present. It is a **single-current-evidence
area**, not a historical warehouse. Each implementation brick may leave only the evidence produced by
the most recent certified brick. Older generated evidence is purged before the new checkpoint closes.

## Retained inside the repository

- `artifacts/current/vX.Y/` for the current brick only;
- only the latest validation/rendered evidence that is useful to inspect the certified work;
- source/documentation required to reproduce validation.

## Purged before certification

- every superseded `artifacts/current/v*/` directory;
- `artifacts/history/` generated evidence;
- `artifacts/releases/` generated evidence/manifests;
- old PNG/SVG boards, JSON dumps, benchmark files and test reports from earlier bricks.

The purge removes generated contents, **not the `artifacts/` directory itself**.

## Release boundary

The certified checkpoint ZIP is delivered outside the project tree. It is not a reason to delete the
current evidence of the brick that the ZIP certifies. The current evidence remains inspectable until
the next brick begins, when it becomes superseded and is purged.

## Exceptions

A file may remain outside the current evidence only when it is a source/reference input required by
the project rather than generated proof. Such an exception must be named in the implementation log.
