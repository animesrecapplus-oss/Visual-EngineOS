from __future__ import annotations

from visual_engine.components.common.geometry_contract import GeometryPath
from visual_engine.entities import build_human_face
from visual_engine.runtime import ProductionRenderSession, path_to_region
from visual_engine.runtime.coverage import DepthRelation, Occluder
from visual_engine.runtime.visibility import resolve_visibility
from visual_engine.scene.composition import Camera, Placement
from visual_engine.math import Vec2


def _request(session: ProductionRenderSession):
    return session.render_face(
        "face-01",
        placement=Placement("face-01", Vec2(450.0, 450.0), scale=650.0),
        camera=Camera(),
        generator="face.human_with_eyes_nose",
    )


def test_v147_closed_bezier_path_is_a_real_area_region() -> None:
    path = GeometryPath((
        ("M", (0.0, 0.0)),
        ("C", (0.0, 10.0, 10.0, 10.0, 10.0, 0.0)),
        ("Z", ()),
    ))
    region = path_to_region(path)
    assert not region.is_empty
    assert region.area > 1.0


def test_v147_generic_region_provider_materializes_closed_surfaces_only() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
        head = result.visibility.target_regions
        nose = result.visibility.occluder_regions
        assert any(r.name == "HEAD" for r in head.regions)
        assert any(r.name == "NOSE" for r in nose.regions)
        assert not any(r.name == "NOSE_DETAIL" for r in nose.regions)


def test_v147_production_overlap_reports_depth_coverage_visibility_and_dominance() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
        visibility = result.visibility
        assert visibility is not None
        assert visibility.target_depth == 0.0
        assert visibility.occluder_depth == 1.0
        assert visibility.depth_relation is DepthRelation.FRONT
        assert 0.0 < visibility.visibility.overall_coverage < 1.0
        assert visibility.visibility.overall_visible < 1.0
        attrs = [a for _, values in visibility.attribution.regions for a in values]
        assert len(attrs) == 1
        assert attrs[0].occluder_id == "nose"
        assert abs(attrs[0].dominant_coverage - attrs[0].coverage) <= 1e-12
        assert attrs[0].coverage > 0.0


def test_v147_depth_reversal_removes_occlusion_in_existing_kernel() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
        target = result.visibility.target_regions
        nose_geometry = result.visibility.occluder_regions.regions[0].geometry
        reversed_result = resolve_visibility(
            "face-01", target, (Occluder("nose", nose_geometry, z=-1.0),), target_z=0.0
        )
        assert reversed_result.overall_coverage == 0.0
        assert reversed_result.overall_visible == 1.0


def test_v147_no_overlap_has_full_target_visibility() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
        target = result.visibility.target_regions
        nose_geometry = result.visibility.occluder_regions.regions[0].geometry
        # Translate the exact nose region outside the target bounds without changing its shape.
        from visual_engine.runtime.geometry_transform import transform_geometry_contract
        translated = transform_geometry_contract(
            nose_geometry,
            ((1.0, 0.0, 10_000.0), (0.0, 1.0, 10_000.0), (0.0, 0.0, 1.0)),
            coordinate_frame=nose_geometry.coordinate_frame,
        )
        no_overlap = resolve_visibility(
            "face-01", target, (Occluder("nose", translated, z=1.0),), target_z=0.0
        )
        assert no_overlap.overall_coverage == 0.0
        assert no_overlap.overall_visible == 1.0


def test_v147_depth_metadata_is_consumed_by_renderer_order() -> None:
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
        indices = {
            surface.name: int(surface.data["path_index"])
            for surface in result.camera_geometry.surfaces
            if surface.name in {"head:head", "nose:nose"}
        }
        assert result.camera_geometry.paths[indices["head:head"]].commands[-1][0] == "Z"
        assert result.camera_geometry.paths[indices["nose:nose"]].commands[-1][0] == "Z"
        depths = {
            surface.name: int(surface.data["depth_layer"])
            for surface in result.camera_geometry.surfaces
            if surface.name in {"head:head", "nose:nose"}
        }
        assert depths == {"head:head": 0, "nose:nose": 1}
        head_index = indices["head:head"]
        nose_index = indices["nose:nose"]
        def path_d(index: int) -> str:
            chunks = []
            for command, values in result.camera_geometry.paths[index].commands:
                chunks.append(command + (" " + " ".join(f"{value:.6f}" for value in values) if values else ""))
            return " ".join(chunks)
        assert result.svg.find(path_d(head_index)) < result.svg.find(path_d(nose_index))


def test_v159_coplanar_occlusion_preserves_coplanar_depth_relation():
    root = build_human_face("face-01")
    with ProductionRenderSession(root) as session:
        result = _request(session)
        target = result.visibility.target_regions
        nose_geometry = result.visibility.occluder_regions.regions[0].geometry
        coplanar = resolve_visibility(
            "face-01", target, (Occluder("nose", nose_geometry, z=0.0),),
            target_z=0.0, coplanar_occludes=True,
        )
    assert coplanar.overall_coverage > 0.0
    assert coplanar.regions[0].depth_relation is DepthRelation.COPLANAR
    assert coplanar.events[0].depth_relation is DepthRelation.COPLANAR
