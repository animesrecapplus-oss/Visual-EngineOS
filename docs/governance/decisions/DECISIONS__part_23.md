# Decisions — V1.89

- `DEC-GAZE-001`: select Gaze after fresh horizontal evidence of a real production/public consumer path and reproducible constructor defects.
- `DEC-GAZE-002`: keep the change local to `Gaze.__post_init__`; do not change the solver algorithm or shared validation helper.
- `DEC-GAZE-003`: retain `_finite` because `BinocularGazeSolver` still consumes it; an attempted removal was caught by direct consumer tests and reverted.
- `DEC-GAZE-004`: enforce the declared immutable tuple target boundary without coercion.
- `DEC-GAZE-005`: preserve valid direction and magnitude semantics; no new optical behavior.
- `DEC-GAZE-006`: optimize only after measurement by reducing duplicate local validation passes; correctness and traceability remain unchanged.
