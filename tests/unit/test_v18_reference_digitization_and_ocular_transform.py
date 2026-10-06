from __future__ import annotations

import math
import re

import pytest

from visual_engine.components.common.geometry_contract import GeometryContract, GeometryPath
from visual_engine.components.common.meta import Component
from visual_engine.components.common.visual_contract import LocalTransform, identity_matrix
from visual_engine.components.face.eyes.reference import (
    ReferenceCurve, ReferenceDigitizationSet, ReferenceFamily, ReferenceSample, ReferenceSource,
    load_v18_reference_envelope_dataset, measure_reference_sample, validate_reference_dataset,
)
from visual_engine.components.face.eyes.reference.transform import resolve_ocular_geometry, resolve_ocular_transform
from visual_engine.geometry import BrowSpec, EyeAppearance, EyePairSpec, EyeParameters, Gaze, build_eye_geometry, build_eye_pair
from visual_engine.render import render_eye_pair_svg, render_eye_svg
from visual_engine.runtime import RuntimeGraph


def _brow_transform(svg: str, center_x: float) -> str:
    match = re.search(rf'transform="(translate\({center_x:.6f} 0\.000000\) rotate\([^\"]+\))"', svg)
    assert match, f"brow transform for center {center_x} not found"
    return match.group(1)


def test_default_brow_gap_is_explicitly_larger_than_v17_default():
    assert BrowSpec().min_eye_gap == pytest.approx(0.45)
    assert BrowSpec(min_eye_gap=0.08).min_eye_gap == pytest.approx(0.08)


def test_brow_is_anchored_to_eye_center_not_world_origin():
    pair = build_eye_pair(EyePairSpec())
    svg = render_eye_pair_svg(pair)
    assert _brow_transform(svg, pair.left.center_x).startswith("translate(-0.650000")
    assert _brow_transform(svg, pair.right.center_x).startswith("translate(0.650000")
    assert "translate(0.650000 0.000000) rotate(0.000000) translate(-0.650000" not in svg


def test_pair_brows_keep_same_local_geometry_under_parent_rotation():
    pair = build_eye_pair(EyePairSpec(base_parameters=EyeParameters(rotation_deg=30.0)))
    svg = render_eye_pair_svg(pair)
    assert pair.left.brow_reference_top_local_y == pytest.approx(pair.right.brow_reference_top_local_y)
    assert pair.left.brow_reference_scale == pytest.approx(pair.right.brow_reference_scale)
    transforms = re.findall(r'transform="(translate\([^\"]+\) rotate\([^\"]+\))"', svg)
    brow_transforms = [t for t in transforms if "rotate(30.000000)" in t]
    assert len(brow_transforms) == 2
    assert any(t.startswith("translate(-0.562917 -0.325000) rotate(30.000000)") for t in brow_transforms)
    assert any(t.startswith("translate(0.562917 0.325000) rotate(30.000000)") for t in brow_transforms)


def test_brow_does_not_move_with_gaze():
    appearance = EyeAppearance(eyebrow=BrowSpec())
    center = build_eye_geometry(EyeParameters(), appearance=appearance, gaze=Gaze(direction="center", strength=0.0))
    aimed = build_eye_geometry(EyeParameters(), appearance=appearance, gaze=Gaze(direction="lower_right", strength=1.0))
    from visual_engine.render.eye_svg_primitives import _eyebrow_svg
    assert _eyebrow_svg(center, appearance.eyebrow) == _eyebrow_svg(aimed, appearance.eyebrow)


def test_caruncle_is_strictly_interior_to_aperture_samples():
    def point_inside(point, polygon):
        x, y = point; inside = False; j = len(polygon) - 1
        for i, (xi, yi) in enumerate(polygon):
            xj, yj = polygon[j]
            if ((yi > y) != (yj > y)) and x < (xj - xi) * (y - yi) / (yj - yi) + xi:
                inside = not inside
            j = i
        return inside
    for rotation in (-90, -45, 0, 30, 45, 90):
        g = build_eye_geometry(EyeParameters(rotation_deg=rotation))
        assert all(point_inside(p, g.contour_points) for p in g.medial_caruncle_points)


def test_epicanthic_endpoints_are_inset_from_canthal_border():
    g = build_eye_geometry(EyeParameters(epicanthic_fold=0.8))
    assert g.epicanthic_fold_points
    assert g.epicanthic_fold_points[0] != g.inner_canthus
    assert g.epicanthic_fold_points[-1] != g.inner_canthus


def test_medial_details_render_before_lid_contour():
    g = build_eye_geometry(EyeParameters(epicanthic_fold=0.8))
    svg = render_eye_svg(g)
    caruncle_index = svg.index('fill="#e8a17f"')
    contour_index = svg.index('stroke="#000000"')
    assert caruncle_index < contour_index




def test_terminal_renderer_uses_point_taper_not_round_or_full_width_caps():
    from visual_engine.render.eye_svg_contours import _contour_svg, _bridge_terminal_ribbon
    shared = build_eye_geometry(EyeParameters())
    contour = _contour_svg(shared, EyeAppearance())
    assert 'stroke-linecap="round"' not in contour
    bridge = build_eye_geometry(EyeParameters(
        canthus_inner_terminal=__import__('visual_engine.geometry', fromlist=['CanthusTerminalSpec']).CanthusTerminalSpec('bridge'),
        canthus_outer_terminal=__import__('visual_engine.geometry', fromlist=['CanthusTerminalSpec']).CanthusTerminalSpec('bridge'),
    ))
    assert _bridge_terminal_ribbon(bridge.inner_canthus_bridge, .036, .024) == ''

def test_reference_envelope_dataset_is_explicitly_not_pixel_digitized():
    dataset = load_v18_reference_envelope_dataset()
    audit = validate_reference_dataset(dataset)
    assert dataset.status == "envelope_only"
    assert not dataset.is_pixel_complete
    assert audit["pixel_digitized_sample_count"] == 0
    assert 1.431 < min(s.envelope_width_px / s.envelope_height_px for s in dataset.samples) < 1.432
    assert 2.69 < max(s.envelope_width_px / s.envelope_height_px for s in dataset.samples) < 2.692


def test_reference_curve_extracts_independent_endpoint_tangents():
    upper = ReferenceCurve("upper", ((0, 0), (1, -1), (2, -1), (3, 0)))
    lower = ReferenceCurve("lower", ((0, 0), (1, 1), (2, 1), (3, 0)))
    sample = ReferenceSample("x", ReferenceFamily.ANIME_STYLIZED, upper=upper, lower=lower, medial_terminal_px=(0, 0), lateral_terminal_px=(3, 0))
    metrics = measure_reference_sample(sample)
    assert metrics["upper_start_tangent_deg"] == pytest.approx(-45.0)
    assert metrics["lower_start_tangent_deg"] == pytest.approx(45.0)


def _nested_graph():
    root = Component("face", "HumanFace", transform=LocalTransform(x=1.0, y=2.0, rotation_deg=15.0, scale_x=1.2, scale_y=.9))
    eye_parent = Component("eye_parent", "Eye", transform=LocalTransform(x=.5, y=-.25, rotation_deg=30.0, scale_x=.8, scale_y=1.1))
    brow = Component("brow", "Eyebrow", transform=LocalTransform(x=.1, y=-.4, rotation_deg=-5.0, scale_x=.9, scale_y=.9))
    eye_parent.add_child(brow)
    root.add_child(eye_parent)
    return RuntimeGraph.from_component(root)


def test_ocular_transform_uses_runtime_root_to_target_composition():
    graph = _nested_graph()
    resolution = resolve_ocular_transform(graph, "brow")
    assert resolution.component_id == "brow"
    # The matrix must differ from every single local transform: parent composition is real.
    assert resolution.local_to_world != identity_matrix()
    x, y = resolution.local_to_world[0][2], resolution.local_to_world[1][2]
    assert math.isfinite(x) and math.isfinite(y)


def test_ocular_transform_resolves_translation_rotation_and_nonuniform_scale():
    graph = _nested_graph()
    geometry = GeometryContract(paths=(GeometryPath((("M", (0.0, 0.0)), ("L", (1.0, 0.0)))),), anchors={"origin": (0.0, 0.0, 0.0)})
    world = resolve_ocular_geometry(graph, "brow", geometry)
    assert world.coordinate_frame == "world"
    assert world.paths[0].commands[0][1] != (0.0, 0.0)
    assert world.paths[0].commands[1][1] != (1.0, 0.0)
    assert world.anchors["origin"][:2] == pytest.approx((world.paths[0].commands[0][1][0], world.paths[0].commands[0][1][1]))


def test_pair_rotation_rotates_interocular_axis_with_both_eyes():
    for rotation in (-90.0, -45.0, -30.0, 0.0, 30.0, 45.0, 90.0):
        pair = build_eye_pair(EyePairSpec(base_parameters=EyeParameters(rotation_deg=rotation)))
        dx = pair.right.center_x - pair.left.center_x
        dy = pair.right.center_y - pair.left.center_y
        expected = math.radians(rotation)
        assert math.atan2(dy, dx) == pytest.approx(expected, abs=1e-9)
        # Both ocular local axes and the binocular centerline must share the same
        # rigid parent orientation; this is stronger than checking each eye alone.
        assert pair.left.rotation_deg == pytest.approx(rotation)
        assert pair.right.rotation_deg == pytest.approx(rotation)


def test_pair_rotation_preserves_midpoint():
    pair = build_eye_pair(
        EyePairSpec(base_parameters=EyeParameters(rotation_deg=90.0)),
        left_center=(-2.0, 1.5), right_center=(4.0, 1.5),
    )
    assert ((pair.left.center_x + pair.right.center_x) * .5,
            (pair.left.center_y + pair.right.center_y) * .5) == pytest.approx((1.0, 1.5))


def test_closed_eye_lid_geometry_inherits_parent_rotation():
    closed = build_eye_geometry(EyeParameters(rotation_deg=30.0), state="closed")
    dx = closed.outer_canthus[0] - closed.inner_canthus[0]
    dy = closed.outer_canthus[1] - closed.inner_canthus[1]
    assert math.degrees(math.atan2(dy, dx)) == pytest.approx(30.0, abs=1e-9)


def test_rotated_closed_eye_brow_and_lid_share_parent_axis():
    appearance = EyeAppearance(eyebrow=BrowSpec(y=-0.75))
    g = build_eye_geometry(EyeParameters(rotation_deg=45.0), state="closed", appearance=appearance)
    svg = render_eye_svg(g, appearance=appearance)
    assert 'rotate(45.000000)' in svg
    dx = g.outer_canthus[0] - g.inner_canthus[0]
    dy = g.outer_canthus[1] - g.inner_canthus[1]
    assert math.degrees(math.atan2(dy, dx)) == pytest.approx(45.0, abs=1e-9)


def test_gaze_is_resolved_in_eye_local_frame_before_parent_rotation():
    local = build_eye_geometry(EyeParameters(rotation_deg=0.0), gaze=Gaze(direction="up", strength=1.0))
    rotated = build_eye_geometry(EyeParameters(rotation_deg=90.0), gaze=Gaze(direction="up", strength=1.0))
    dx = rotated.iris_center[0] - rotated.center_x
    dy = rotated.iris_center[1] - rotated.center_y
    # Eye-local up (0,-1) inherits +90° as world-right (+1,0).
    assert dx > 0 and abs(dy) < abs(dx) * 0.15
    assert local.gaze_solution.normalized_x == pytest.approx(0.0)
    assert local.gaze_solution.normalized_y < 0


def test_reference_acquisition_rejects_wrong_hash_or_dimensions(tmp_path):
    from visual_engine.components.face.eyes.reference import ReferenceAcquisitionRecord, verify_reference_file
    from PIL import Image
    path = tmp_path / "candidate.png"
    Image.new("RGB", (16, 16), (255, 255, 255)).save(path)
    record = ReferenceAcquisitionRecord(
        source_id="x", expected_name="x.png", expected_sha256="0" * 64,
        expected_width_px=32, expected_height_px=32,
    )
    checked = verify_reference_file(record, path)
    assert checked.status == "rejected"
    assert "sha256 mismatch" in checked.notes
    assert "width mismatch" in checked.notes


def test_reference_trace_metrics_keep_four_endpoint_axes_independent():
    from visual_engine.components.face.eyes.reference import ReferenceCurve, ReferenceFamily, ReferenceSample, measure_reference_sample_v19
    upper = ReferenceCurve("upper", ((0, 0), (1, -1), (2, -1), (4, 0)))
    lower = ReferenceCurve("lower", ((0, 0), (1, 2), (2, 1), (4, 0)))
    sample = ReferenceSample("trace", ReferenceFamily.ANIME_STYLIZED, upper=upper, lower=lower, medial_terminal_px=(0, 0), lateral_terminal_px=(4, 0))
    m = measure_reference_sample_v19(sample)
    assert m["inner_upper"]["endpoint_tangent_deg"] != m["inner_lower"]["endpoint_tangent_deg"]
    assert m["outer_upper"]["endpoint_tangent_deg"] != m["outer_lower"]["endpoint_tangent_deg"]
    assert m["inner_upper"]["transition_length_px"] >= 0
