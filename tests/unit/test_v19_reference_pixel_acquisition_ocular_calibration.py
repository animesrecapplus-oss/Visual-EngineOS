from __future__ import annotations

import math

import pytest

from visual_engine.geometry import EyePairSpec, EyeParameters, Gaze, build_eye_geometry, build_eye_pair


def test_pair_axis_rotation_is_rigid_about_midpoint():
    for angle in (-90.0, -45.0, -30.0, 0.0, 30.0, 45.0, 90.0):
        pair = build_eye_pair(EyePairSpec(base_parameters=EyeParameters(rotation_deg=angle)))
        dx = pair.right.center_x - pair.left.center_x
        dy = pair.right.center_y - pair.left.center_y
        assert math.degrees(math.atan2(dy, dx)) == pytest.approx(angle, abs=1e-9)
        assert ((pair.left.center_x + pair.right.center_x) / 2,
                (pair.left.center_y + pair.right.center_y) / 2) == pytest.approx((0.0, 0.0))


def test_pair_rotation_does_not_destroy_medial_symmetry():
    for angle in (-90.0, -45.0, 30.0, 90.0):
        pair = build_eye_pair(EyePairSpec(base_parameters=EyeParameters(rotation_deg=angle)))
        # Relative to each eye's center, the medial terminal must remain on the
        # side facing the pair midpoint after the rigid parent rotation.
        mx = (pair.left.center_x + pair.right.center_x) / 2
        for eye in (pair.left, pair.right):
            medial_vector = (eye.inner_canthus[0] - eye.center_x, eye.inner_canthus[1] - eye.center_y)
            center_vector = (mx - eye.center_x, (pair.left.center_y + pair.right.center_y) / 2 - eye.center_y)
            assert medial_vector[0] * center_vector[0] + medial_vector[1] * center_vector[1] > 0


def test_closed_lid_inherits_rotation():
    for angle in (-90.0, -45.0, 30.0, 90.0):
        g = build_eye_geometry(EyeParameters(rotation_deg=angle), state="closed")
        dx = g.outer_canthus[0] - g.inner_canthus[0]
        dy = g.outer_canthus[1] - g.inner_canthus[1]
        assert math.degrees(math.atan2(dy, dx)) == pytest.approx(angle, abs=1e-9)


def test_gaze_direction_is_local_then_inherits_rotation():
    g = build_eye_geometry(EyeParameters(rotation_deg=90.0), gaze=Gaze(direction="up", strength=1.0))
    dx = g.iris_center[0] - g.center_x
    dy = g.iris_center[1] - g.center_y
    assert dx > 0 and abs(dy) < abs(dx) * .15


def test_segmentation_proposes_cells_without_fixed_grid_assumption(tmp_path):
    from PIL import Image, ImageDraw
    from visual_engine.components.face.eyes.reference import segment_reference_sheet
    path = tmp_path / "sheet.png"
    image = Image.new("RGB", (600, 400), "white")
    draw = ImageDraw.Draw(image)
    for box in ((50, 40, 180, 130), (350, 70, 540, 160), (100, 240, 220, 340), (390, 230, 570, 350)):
        draw.ellipse(box, outline="black", width=8)
    image.save(path)
    result = segment_reference_sheet(path)
    assert result["status"] == "segmentation_candidates_require_visual_review"
    assert result["candidate_count"] == 4
    assert all(isinstance(box["x"], int) for box in result["candidate_boxes_px"])
