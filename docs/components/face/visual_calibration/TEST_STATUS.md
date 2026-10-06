# Test status — CMP-FACE-VIS-001

Dedicated suite: `tests/components/face/visual_calibration/test_v178_face_visual_calibration.py`.

Covered: alignment, nose/mouth spacing, hair silhouette, density bounds, hostile numeric inputs, shape/color/detail variation.

Affected legacy suites: hair, ear, nose, hair/ear relation, head/ear relation, production visual style and face overlap visibility.

Final full regression: 1164 collected; 1163 passed; 1 expected PostgreSQL skip; 0 failures. The full collection was executed in deterministic batches because the monolithic invocation exceeded the execution window.

Final benchmark: V1.77 median 65,516,842.0 ns; V1.78 median 68,673,361.5 ns; +4.818%. No speculative optimization was introduced.
