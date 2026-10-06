from visual_engine.components.common.geometry_contract import GeometryContract, GeometryPrimitive
from visual_engine.runtime.semantic_regions import RegionMap, rectangle_region
from visual_engine.runtime.coverage import DepthRelation, Occluder, resolve_coverage


def rect(x0,y0,x1,y1):
    return GeometryContract(primitives=(GeometryPrimitive("polygon", {"points":((x0,y0),(x1,y0),(x1,y1),(x0,y1))}),))


def test_partial_coverage_identifies_only_intersected_regions():
    regions=RegionMap("eye", (
        rectangle_region("upper", "upper_eyelid", 0, 0.5, 10, 2),
        rectangle_region("iris", "iris", 3, 3, 7, 7),
        rectangle_region("lower", "lower_eyelid", 0, 8, 10, 9.5),
    ))
    result=resolve_coverage("eye", regions, Occluder("hand", rect(0,0,10,4), z=1.0), target_z=0)
    assert result.depth_relation is DepthRelation.FRONT
    assert result.overall_coverage > 0
    by_id={r.region_id:r for r in result.regions}
    assert by_id["upper"].coverage > 0
    assert by_id["iris"].coverage > 0
    assert by_id["lower"].coverage == 0


def test_diagonal_occluder_is_spatial_not_type_specific():
    regions=RegionMap("eye", (rectangle_region("iris","iris",0,0,10,10),))
    diag=rect(5,-5,15,5)
    result=resolve_coverage("eye", regions, Occluder("unknown-object", diag, z=2), target_z=0)
    assert 0 < result.regions[0].coverage < 1


def test_behind_object_does_not_hide_target():
    regions=RegionMap("eye", (rectangle_region("iris","iris",0,0,10,10),))
    result=resolve_coverage("eye", regions, Occluder("object", rect(0,0,10,10), z=-1), target_z=0)
    assert result.depth_relation is DepthRelation.BEHIND
    assert result.regions[0].coverage == 0
    assert result.regions[0].visible == 1


def test_transmission_is_reported_separately_from_geometric_coverage():
    regions=RegionMap("eye", (rectangle_region("iris","iris",0,0,10,10),))
    result=resolve_coverage("eye", regions, Occluder("transparent", rect(0,0,10,5), z=1, opacity=.25, transmission=.8), target_z=0)
    r=result.regions[0]
    assert r.coverage == .5
    # Geometric coverage remains .5. Optical visibility is separately resolved:
    # opacity=.25 and transmission=.8 imply an effective blocking alpha of .05,
    # hence 0.975 visibility across the covered half.
    assert r.visible == .975
    assert r.transmitted_visibility > 0
