from visual_engine.geometry import EyeParameters, CanthusTerminalSpec, build_eye_geometry
from visual_engine.components.face.eyes.geometry.invariants import has_self_intersection


def _build(**kwargs):
    kwargs.setdefault("canthus_inner_terminal", CanthusTerminalSpec("bridge"))
    kwargs.setdefault("canthus_outer_terminal", CanthusTerminalSpec("bridge"))
    return build_eye_geometry(EyeParameters(width=2.0, height=1.0, **kwargs))


def test_inner_and_outer_canthus_roundness_are_independent():
    base = _build()
    inner = _build(canthus_inner_roundness=0.18)
    outer = _build(canthus_outer_roundness=0.18)
    assert inner.inner_canthus != base.inner_canthus
    assert inner.outer_canthus == base.outer_canthus
    assert outer.outer_canthus != base.outer_canthus
    assert outer.inner_canthus == base.inner_canthus


def test_legacy_canthus_roundness_matches_explicit_defaults():
    legacy = _build(canthus_roundness=0.07)
    explicit = _build(canthus_roundness=0.07, canthus_inner_roundness=0.07, canthus_outer_roundness=0.07)
    assert legacy.contour_points == explicit.contour_points


def test_canthus_change_does_not_change_iris_or_pupil_assembly():
    base = _build()
    changed = _build(canthus_inner_roundness=0.18)
    assert changed.iris_center == base.iris_center
    assert changed.iris_rx == base.iris_rx
    assert changed.pupil_center == base.pupil_center


def test_adversarial_morphology_matrix_has_no_self_intersections():
    for shape in ("almond", "round", "large_round", "ellipse", "narrow", "droopy", "sharp", "upturned", "downturned"):
        for opening in (0.02, 0.2, 0.5, 1.0):
            for inner in (0.0, 0.035, 0.2):
                for outer in (0.0, 0.035, 0.2):
                    g = build_eye_geometry(EyeParameters(
                        shape=shape, width=2.0, height=1.0, opening=opening,
                        canthus_inner_roundness=inner, canthus_outer_roundness=outer,
                    ))
                    assert not has_self_intersection(g.contour_points)
