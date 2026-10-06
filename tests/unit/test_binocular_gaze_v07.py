import math

from visual_engine.geometry import (
    BinocularGazeSolver,
    EyeParameters,
    build_binocular_eye_geometries,
)


def test_common_target_produces_opposite_horizontal_gaze_for_convergence():
    left, right, pair = build_binocular_eye_geometries(
        EyeParameters(width=1.0, height=0.5),
        EyeParameters(width=1.0, height=0.5),
        left_center=(-0.6, 0.0),
        right_center=(0.6, 0.0),
        target=(0.0, 0.0),
    )
    assert left.gaze_solution.normalized_x > 0
    assert right.gaze_solution.normalized_x < 0
    assert abs(left.gaze_solution.normalized_y) < 1e-12
    assert abs(right.gaze_solution.normalized_y) < 1e-12
    assert pair.convergence_angle_deg > 0


def test_common_high_target_drives_both_eyes_up():
    left, right, pair = build_binocular_eye_geometries(
        left_center=(-0.6, 0.0), right_center=(0.6, 0.0), target=(0.0, -10.0)
    )
    assert left.gaze_solution.normalized_y < 0
    assert right.gaze_solution.normalized_y < 0
    assert pair.left_angle_deg < 0 and pair.right_angle_deg < 0


def test_asymmetric_morphology_is_solved_independently():
    left, right, _ = build_binocular_eye_geometries(
        EyeParameters(width=1.0, height=0.25, shape="narrow"),
        EyeParameters(width=1.0, height=1.0, shape="large_round"),
        left_center=(-0.6, 0.0), right_center=(0.6, 0.0), target=(0.0, 2.0),
    )
    assert left.gaze_solution.clamped
    assert right.gaze_solution.clamped
    assert right.gaze_solution.limit > left.gaze_solution.limit


def test_pair_solver_reports_small_angular_separation_for_distant_target():
    pair = BinocularGazeSolver.solve((-1.0, 0.0), (1.0, 0.0), (0.0, -10.0))
    assert math.isclose(pair.convergence_angle_deg, 11.421186, rel_tol=1e-5)


def test_pair_solver_rejects_target_at_eye_center():
    try:
        BinocularGazeSolver.solve((-1.0, 0.0), (1.0, 0.0), (-1.0, 0.0))
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError")
