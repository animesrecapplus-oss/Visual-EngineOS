from dataclasses import replace

import pytest

from visual_engine.geometry import (
    EyePairPolicy, EyePairSpec, EyeParameters, IrisSpec, PupilSpec,
    anime_golden, build_eye_pair, make_heterochromic_pair, reflective_scene_eye,
)
from visual_engine.render import render_eye_pair_svg


def test_human_default_pair_is_identical_by_default():
    pair = build_eye_pair()
    assert pair.paired
    assert pair.morphology_match
    assert pair.appearance_match
    assert pair.left_appearance.outline == "#000000"
    assert pair.right_appearance.pupils[0].color == "#000000"
    assert pair.left_appearance.lower_lashes.color == "#666666"


def test_human_default_allows_small_size_asymmetry():
    base = EyeParameters(width=1.0, height=0.55)
    left = replace(base, width=1.05, height=0.58)
    right = replace(base, width=0.97, height=0.52)
    pair = build_eye_pair(EyePairSpec(base_parameters=base, left_parameters=left, right_parameters=right))
    assert pair.paired


def test_human_default_rejects_shape_mismatch():
    base = EyeParameters()
    with pytest.raises(ValueError):
        build_eye_pair(EyePairSpec(base_parameters=base, right_parameters=replace(base, shape="large_round")))


def test_heterochromia_keeps_morphology_identical():
    base = EyeParameters()
    app = anime_golden()
    spec = make_heterochromic_pair(base, app, "#2a78d4")
    pair = build_eye_pair(spec)
    assert pair.morphology_match
    assert pair.left.iris_rx == pair.right.iris_rx
    assert spec.right_appearance.iris.color == "#2a78d4"


def test_free_pair_allows_nonhuman_structural_variation():
    spec = EyePairSpec(
        base_parameters=EyeParameters(),
        right_parameters=EyeParameters(shape="large_round"),
        policy=EyePairPolicy(mode="free"),
    )
    pair = build_eye_pair(spec)
    assert not pair.morphology_match


def test_reference_presets_have_black_outline_and_white_sclera():
    for appearance in (anime_golden(), reflective_scene_eye()):
        assert appearance.outline == "#000000"
        assert appearance.sclera.startswith("#ffffff") or appearance.sclera == "#f5f5e9"
        assert appearance.reflection_marks


def test_pair_svg_is_single_document():
    pair = build_eye_pair(
        EyePairSpec(base_appearance=anime_golden()),
        left_center=(-0.7, 0.0), right_center=(0.7, 0.0), target=(0.0, -2.0),
    )
    svg = render_eye_pair_svg(pair)
    assert svg.startswith("<svg")
    assert svg.endswith("</svg>")
    assert svg.count("<clipPath") == 2
    assert "#f4d20a" in svg


def test_human_pair_profile_applies_to_both_eyes_by_default():
    from visual_engine.geometry import OcularPresentationProfile
    profile = OcularPresentationProfile.preset("child", "neutral")
    spec = EyePairSpec(presentation_profile=profile)
    pair = build_eye_pair(spec)
    assert pair.left.iris_rx == pair.right.iris_rx
    assert pair.left.opening == pair.right.opening


def test_heterochromia_changes_appearance_not_morphology():
    app = anime_golden()
    spec = make_heterochromic_pair(EyeParameters(), app, "#2277dd")
    pair = build_eye_pair(spec)
    assert pair.morphology_match
    assert not pair.appearance_match
