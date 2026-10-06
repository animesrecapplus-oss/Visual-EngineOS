from visual_engine.geometry import *
from visual_engine.render import render_eye_svg


def test_expressive_eye_vertical_slice():
    params=EyeParameters(shape="large_round", width=1.4, height=.9, opening=1.0, contour_wave_amplitude=.12, contour_irregularity=.5)
    appearance=EyeAppearance(
        iris=IrisSpec(shape="circle", color="#6f3cff", pattern="radial", ring_count=3, glow=.7),
        pupils=(PupilSpec(x=0,y=0,shape="diamond",color="#050505"), PupilSpec(x=.22,y=.03,scale=.45,color="#050505")),
        lashes=LashSpec(enabled=True,density=.9,length=.14,count=7),
        eyebrow=BrowSpec(enabled=True,shape="arched",length=.85,thickness=.08,density=.75),
        reflection="#ffffff",
    )
    gaze=Gaze(x=-.9,y=.15)
    geometry=build_eye_geometry(params, state="crying", gaze=gaze, appearance=appearance)
    svg=render_eye_svg(geometry, appearance=appearance)
    assert geometry.state == "crying"
    assert len(geometry.pupil_centers)==2
    assert "clipPath" in svg
