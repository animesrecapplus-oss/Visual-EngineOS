# Prechange impact audit — CMP-VBOOL-001

## VERIFY

The certified V1.74 checkpoint was inspected together with current status, roadmap, architecture tree, decision register,
V1.74 placement-coverage truth dossier, implementation protocol and artifact-retention policy. The repository was clean
before modification and `artifacts/current/v1.74/` was the only retained current artifact boundary.

## Fresh read-only responsibility audit

`runtime/visibility.py` is 294 lines and contains two independently bounded responsibilities:

1. boolean planar composition (`BooleanOperation`, `BooleanResult`, union/intersection/difference operations);
2. multi-occluder visibility resolution and visibility-event emission.

The boolean responsibility is a real public runtime API. The compatibility facade and package API consume it after extraction; the
production visibility resolver remains deliberately unchanged because its hot path already performs the same low-level Shapely operations.
This is a bounded public-contract extraction, not a speculative renderer/helper split.

## Real consumers

- `runtime.visibility.resolve_visibility` consumes the extracted low-level boolean region operations.
- `runtime.__init__` exposes the public boolean API.
- Existing unit tests consume the historical `runtime.visibility` import path.
- `runtime.visibility_attribution` independently consumes region materialization and is not changed.
- Production occlusion modules consume `VisibilityResult`/`resolve_visibility`, not the boolean public helpers directly.

## Impact

Affected: `runtime/visibility.py`, new `runtime/visibility_boolean.py`, `runtime/__init__.py`, dedicated tests and
truth/governance evidence.

Frozen: visibility event/result contracts, depth ordering, optical transmission, occlusion semantics, region geometry
conversion, cache/fingerprint/provenance, persistence/database, COLOR, renderer/session lifecycle and public legacy
imports.

Visual impact is potentially reachable through the production visibility path, so production normal/boundary/interaction
visual QA is mandatory. Database impact is expected to be none, but must be re-audited after implementation.

## IMPACT REOPENED DURING IMPLEMENTATION

The first implementation routed the hot `resolve_visibility` loop through new Python-level low-level boolean helpers. Fresh-process benchmark
showed a +11.941% median regression versus V1.74. This was treated as new evidence, not ignored.

The scope was reopened and corrected: the canonical owner retains the public boolean composition contract/functions, while the established
hot visibility loop keeps its direct Shapely calls. The production path therefore has no additional Python helper-call overhead and its
semantics remain unchanged. A second fresh-process benchmark measured -6.287% median versus V1.74 in the final sample.

The correction is recorded in `ERR-VBOOL-001` and `DEC-VBOOL-003`; the initial implementation was not certified.
