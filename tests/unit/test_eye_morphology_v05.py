from visual_engine.geometry import *
import math


def test_shape_family_changes_envelope():
    almond=build_eye_geometry(EyeParameters(shape="almond"))
    round_eye=build_eye_geometry(EyeParameters(shape="large_round"))
    assert round_eye.visible_height > almond.visible_height


def test_gaze_stays_inside_conservative_eye_region():
    a=EyeAppearance(pupils=(PupilSpec(x=0,y=0),))
    g=build_eye_geometry(EyeParameters(width=2,height=1), gaze=Gaze(100,100), appearance=a)
    px,py=g.pupil_centers[0]
    cx,cy=g.iris_center
    assert ((px-cx)/(g.nominal_width*.39))**2 + ((py-cy)/(g.visible_height*.39))**2 <= 1.000001


def test_multiple_pupils_are_supported():
    a=EyeAppearance(pupils=(PupilSpec(x=-.15,color="#f00"),PupilSpec(x=.15,color="#0ff")))
    g=build_eye_geometry(EyeParameters(), appearance=a)
    assert len(g.pupil_centers)==2


def test_iris_can_have_rings_and_glow():
    a=EyeAppearance(iris=IrisSpec(ring_count=3, glow=.8, pattern="radial"))
    g=build_eye_geometry(appearance=a)
    assert a.iris.ring_count == 3 and a.iris.glow == .8
    assert g.iris_rx > 0


def test_lashes_and_brow_are_independently_optional():
    a=EyeAppearance(lashes=LashSpec(enabled=False), eyebrow=BrowSpec(enabled=False))
    assert not a.lashes.enabled and not a.eyebrow.enabled


def test_named_gaze_directions_move_the_complete_iris_pupil_assembly():
    center = build_eye_geometry(EyeParameters(width=2, height=1), gaze=Gaze(direction="center"))
    up = build_eye_geometry(EyeParameters(width=2, height=1), gaze=Gaze(direction="up"))
    down = build_eye_geometry(EyeParameters(width=2, height=1), gaze=Gaze(direction="down"))
    left = build_eye_geometry(EyeParameters(width=2, height=1), gaze=Gaze(direction="left"))
    right = build_eye_geometry(EyeParameters(width=2, height=1), gaze=Gaze(direction="right"))
    cx, cy = center.pupil_center
    assert up.pupil_center[1] < cy
    assert down.pupil_center[1] > cy
    assert left.pupil_center[0] < cx
    assert right.pupil_center[0] > cx
    for g in (up, down, left, right):
        assert math.isfinite(g.pupil_center[0]) and math.isfinite(g.pupil_center[1])
        assert g.gaze_solution.limit > 0


def test_gaze_diagonal_keeps_pupil_centered_in_iris():
    g = build_eye_geometry(EyeParameters(width=2, height=1), gaze=Gaze(direction="upper_right"))
    assert g.gaze_solution.clamped


def test_sclera_marks_and_under_eye_marks_are_represented():
    a = EyeAppearance(
        sclera_spots=((-.2, .05, .03, "#ff0000"),),
        under_eye_marks=((-0.2, 1.1, .4, .03, "#552222"),),
        stress_intensity=.9,
    )
    svg = __import__("visual_engine.render", fromlist=["render_eye_svg"]).render_eye_svg(
        build_eye_geometry(), appearance=a
    )
    assert "#ff0000" in svg and "#552222" in svg


def test_rotation_changes_contour_coordinates():
    a = build_eye_geometry(EyeParameters(rotation_deg=0))
    b = build_eye_geometry(EyeParameters(rotation_deg=20))
    assert a.contour_points != b.contour_points
