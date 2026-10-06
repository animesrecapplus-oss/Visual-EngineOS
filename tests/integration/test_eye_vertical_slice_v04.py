from visual_engine.entities.face import build_eye
from visual_engine.geometry import EyeParameters, build_eye_geometry
from visual_engine.render import render_eye_svg


def test_v04_eye_vertical_slice():
    component = build_eye("eye", x=0.0)
    p = EyeParameters(
        width=component.parameters["width"].value,
        height=component.parameters["height"].value,
        opening=component.parameters["opening"].value,
        iris_ratio=component.parameters["iris_ratio"].value,
        pupil_ratio=component.parameters["pupil_ratio"].value,
        asymmetry=component.parameters["asymmetry"].value,
    )
    geometry = build_eye_geometry(p)
    svg = render_eye_svg(geometry)
    assert geometry.nominal_width > 0
    assert geometry.visible_height > 0
    assert len(svg) > 500
    assert component.find("eye__cornea") is not None
    assert component.find("eye__tear_system") is not None
