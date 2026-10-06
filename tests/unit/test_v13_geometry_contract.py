from visual_engine.model import (
    Component,
    GeometryBounds,
    GeometryContract,
    GeometryMask,
    GeometryPath,
    GeometryPrimitive,
    GeometrySurface,
    geometry_hash,
)
from visual_engine.runtime.graph import RuntimeGraph


def test_generic_geometry_contract_accepts_primitives_paths_surfaces_masks_and_anchors():
    geometry = GeometryContract(
        coordinate_frame="component_local",
        bounds=GeometryBounds(-2, -1, 4, 5),
        primitives=(GeometryPrimitive("ellipse", {"cx": 1, "cy": 2, "rx": 3, "ry": 4}),),
        paths=(GeometryPath((("M", (0, 0)), ("C", (1, 2, 3, 4, 5, 6)), ("Z", ()))),),
        surfaces=(GeometrySurface("cornea", {"normal": (0, 0, 1)}),),
        masks=(GeometryMask("eyelid_clip", "clip", {"id": "m1"}),),
        anchors={"center": (1, 2, 0)},
        local_z=0.25,
    )
    assert geometry.bounds.max_x == 4
    assert geometry.primitives[0].kind == "ellipse"
    assert geometry.paths[0].commands[1][0] == "C"
    assert geometry.surfaces[0].name == "cornea"
    assert geometry.masks[0].operation == "clip"
    assert geometry.anchors["center"] == (1.0, 2.0, 0.0)


def test_geometry_hash_is_stable_and_changes_when_geometry_changes():
    a = GeometryContract(primitives=(GeometryPrimitive("circle", {"r": 2}),))
    b = GeometryContract(primitives=(GeometryPrimitive("circle", {"r": 2}),))
    c = GeometryContract(primitives=(GeometryPrimitive("circle", {"r": 3}),))
    assert geometry_hash(a) == geometry_hash(b)
    assert geometry_hash(a) != geometry_hash(c)


def test_component_has_generic_geometry_contract():
    root = Component("root", "head", geometry=GeometryContract(local_z=1))
    eye = Component("eye", "eye", geometry=GeometryContract(primitives=(GeometryPrimitive("ellipse", {"rx": 10, "ry": 5}),)))
    root.add_child(eye)
    graph = RuntimeGraph.from_component(root)
    assert graph.get("eye").component.geometry.primitives[0].kind == "ellipse"


def test_geometry_rejects_non_finite_payload():
    import math
    try:
        GeometryPrimitive("bad", {"x": math.inf})
    except ValueError:
        pass
    else:
        raise AssertionError("non-finite geometry payload must be rejected")


def test_geometry_path_rejects_wrong_command_arity():
    import pytest
    with pytest.raises(ValueError):
        GeometryPath((("C", (1, 2)),))


def test_geometry_path_rejects_unknown_command():
    import pytest
    with pytest.raises(ValueError):
        GeometryPath((("R", (1, 2)),))
