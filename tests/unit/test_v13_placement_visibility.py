from __future__ import annotations

from visual_engine.components.common.geometry_contract import GeometryBounds, GeometryContract, GeometryPrimitive
from visual_engine.components.common.meta import Component
from visual_engine.runtime.placement import PlacementSolution
from visual_engine.runtime.placement_visibility import resolve_placement_visibility
from visual_engine.runtime.semantic_regions import RegionMap, SemanticRegion, rectangle_region


def rect(min_x, min_y, max_x, max_y, *, frame="scene"):
    return GeometryContract(
        coordinate_frame=frame,
        bounds=GeometryBounds(min_x, min_y, max_x, max_y),
        primitives=(GeometryPrimitive("polygon", {"points": ((min_x,min_y),(max_x,min_y),(max_x,max_y),(min_x,max_y)), "semantic_region": "body"}),),
        anchors={"origin": (min_x, min_y, 0.0)},
    )


def test_placement_materializes_source_and_resolves_partial_target_impact_without_object_types():
    source = Component(id="source-object", kind="arbitrary-source")
    source_geometry = rect(0, 0, 4, 4, frame="local")
    target_regions = RegionMap("arbitrary-target", (
        SemanticRegion("top", "top", rect(0, 0, 10, 5, frame="scene")),
        SemanticRegion("bottom", "bottom", rect(0, 5, 10, 10, frame="scene")),
    ))
    placement = PlacementSolution(
        source_id=source.id,
        target_id="arbitrary-target",
        translation=(3.0, 0.0),
        rotation_deg=0.0,
        scale_x=1.0,
        scale_y=1.0,
        z_offset=1.0,
        source_anchor=(0.0, 0.0, 0.0),
        target_anchor=(3.0, 0.0, 0.0),
    )

    result = resolve_placement_visibility(source, source_geometry, placement, target_regions)

    assert result.source_geometry.coordinate_frame == "scene"
    assert result.source_regions.target_id == source.id
    assert result.source_regions.regions[0].geometry.coordinate_frame == "scene"
    assert result.visibility.overall_coverage > 0.0
    assert result.visibility.overall_coverage < 1.0
    assert any(e.region_id == "top" for e in result.events)
    assert not any(e.region_id == "bottom" and e.intersection_area > 0 for e in result.events)


def test_rotation_and_translation_are_applied_once_to_source_regions_and_geometry():
    source = Component(id="source", kind="object-a")
    geometry = rect(0, 0, 2, 1, frame="local")
    target_regions = RegionMap("target", (rectangle_region("target-region", "surface", 0, 0, 20, 20),))
    placement = PlacementSolution(
        source_id="source", target_id="target", translation=(10, 10),
        rotation_deg=90, scale_x=2, scale_y=2, z_offset=2,
        source_anchor=(0, 0, 0), target_anchor=(10, 10, 0),
    )

    result = resolve_placement_visibility(source, geometry, placement, target_regions)
    bounds = result.source_geometry.bounds
    assert round(bounds.min_x, 6) == 8.0
    assert round(bounds.max_x, 6) == 10.0
    assert round(bounds.min_y, 6) == 10.0
    assert round(bounds.max_y, 6) == 14.0
    assert result.source_geometry.local_z == 2.0


def test_behind_placement_produces_no_occlusion_event():
    source = Component(id="behind", kind="unrelated")
    geometry = rect(0, 0, 10, 10, frame="local")
    target = RegionMap("target", (rectangle_region("surface", "surface", 0, 0, 10, 10),))
    placement = PlacementSolution(
        source_id="behind", target_id="target", translation=(0, 0),
        rotation_deg=0, scale_x=1, scale_y=1, z_offset=-1,
        source_anchor=(0, 0, 0), target_anchor=(0, 0, 0),
    )
    result = resolve_placement_visibility(source, geometry, placement, target)
    assert result.visibility.overall_coverage == 0.0
    assert result.events == ()
