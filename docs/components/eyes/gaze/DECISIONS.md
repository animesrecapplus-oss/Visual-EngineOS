# Decisions — CMP-EYE-GAZE

- `DEC-GAZE-001`: select Gaze after a fresh horizontal audit because a real public/production consumer path and
  reproducible constructor defects are both verified.
- `DEC-GAZE-002`: harden only `Gaze.__post_init__`; do not change `GazeSolver` math or shared validation semantics.
- `DEC-GAZE-003`: retain the shared `_finite` import because `BinocularGazeSolver` still consumes it; removing it
  during local hardening caused verified integration failures and was immediately corrected.
- `DEC-GAZE-004`: require target tuple shape/type at the local boundary because the declared API is a tuple and the
  frozen value object must not silently retain a mutable list target.
- `DEC-GAZE-005`: preserve all existing valid magnitude ranges and named direction semantics; no new optical behavior.
- `DEC-GAZE-006`: optimize only after measurement. The first correction measured +135.898% versus V1.88; one-pass
  validation reduced that to +89.357%, and a measured built-in numeric fast path then produced -10.894% versus V1.88.
  The final resource benchmark measured -17.504% CPU time, +21.218% throughput and -31.169% peak memory in the
  diagnostic workload. No semantic coercion or relaxed invariant was used.
