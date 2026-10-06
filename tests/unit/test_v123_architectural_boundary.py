from __future__ import annotations

import ast
from pathlib import Path

import pytest

from visual_engine.components.common.meta import Component, Parameter
from visual_engine.components.common.visual_contract import LocalTransform
from visual_engine.components.face.eyes.geometry.runtime_transform import resolve_ocular_basis, resolve_alignment_axis_rotation
from visual_engine.runtime import RuntimeGraph, resolve_geometry_transform

ROOT = Path(__file__).resolve().parents[2]


def test_generic_local_transform_contains_no_ocular_semantics():
    fields = set(LocalTransform.__dataclass_fields__)
    assert fields == {"x", "y", "rotation_deg", "scale_x", "scale_y", "z"}
    with pytest.raises(TypeError):
        LocalTransform(ocular_yaw_deg=20)  # type: ignore[call-arg]


def test_generic_geometry_resolution_does_not_execute_ocular_resolution():
    root = Component("root", "ArbitraryThing", transform=LocalTransform(rotation_deg=25))
    child = Component("child", "FutureThing", transform=LocalTransform(x=2))
    root.add_child(child)
    resolved = resolve_geometry_transform(RuntimeGraph.from_component(root), "child")
    assert not hasattr(resolved, "ocular_basis")
    assert not hasattr(resolved, "alignment_axis_rotation_deg")


def test_eye_adapter_consumes_ocular_parameters_without_changing_generic_matrix():
    root = Component(
        "root", "Head",
        transform=LocalTransform(rotation_deg=20),
        parameters={
            "ocular_yaw_deg": Parameter("ocular_yaw_deg", 30),
            "alignment_axis_rotation_deg": Parameter("alignment_axis_rotation_deg", 10),
        },
    )
    eye = Component(
        "eye", "Eye",
        transform=LocalTransform(x=2, rotation_deg=5),
        parameters={
            "ocular_pitch_deg": Parameter("ocular_pitch_deg", 15),
            "alignment_axis_rotation_deg": Parameter("alignment_axis_rotation_deg", 5),
        },
    )
    root.add_child(eye)
    graph = RuntimeGraph.from_component(root)
    generic = resolve_geometry_transform(graph, "eye")
    basis = resolve_ocular_basis(graph, "eye")
    assert generic.local_to_world[0][2] == pytest.approx(2 * __import__("math").cos(__import__("math").radians(20)))
    assert basis.view_axis != pytest.approx((0.0, 0.0, 1.0))
    assert resolve_alignment_axis_rotation(graph, "eye") == pytest.approx(15)


def test_generic_runtime_has_no_static_eye_specific_import():
    path = ROOT / "src" / "visual_engine" / "runtime" / "geometry_transform.py"
    tree = ast.parse(path.read_text(encoding="utf-8"))
    forbidden = "visual_engine.components.face.eyes"
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            assert not module.startswith(forbidden), ast.unparse(node)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                assert not alias.name.startswith(forbidden), ast.unparse(node)


def test_legacy_serialized_ocular_transform_is_migrated_to_parameters():
    from visual_engine.persistence.serialization import component_from_payload

    component = component_from_payload(
        "eye",
        "Eye",
        None,
        {},
        {},
        {
            "transform": {
                "x": 0,
                "y": 0,
                "rotation_deg": 7,
                "scale_x": 1,
                "scale_y": 1,
                "z": 0,
                "ocular_yaw_deg": 60,
                "ocular_pitch_deg": -20,
                "alignment_axis_rotation_deg": 25,
            },
            "visual": {
                "fill_color": "#ffffff",
                "contour": {"color":"#000000","width":1,"opacity":1,"style":"solid","cap":"round","join":"round"},
                "material": {"name":"default","roughness":1,"metallic":0,"transmission":0,"emission":0},
                "opacity": 1,
                "visibility": 1,
            },
            "geometry": {
                "coordinate_frame":"component",
                "bounds":{"min_x":0,"min_y":0,"max_x":1,"max_y":1},
                "primitives":[],"paths":[],"surfaces":[],"masks":[],"anchors":{},"local_z":0,
            },
        },
    )
    assert component.transform.rotation_deg == 7
    assert component.parameters["ocular_yaw_deg"].value == 60
    assert component.parameters["ocular_pitch_deg"].value == -20
    assert component.parameters["alignment_axis_rotation_deg"].value == 25


def test_legacy_transform_parameter_conflict_fails_closed():
    from visual_engine.persistence.serialization import component_from_payload

    metadata = {
        "transform": {
            "x":0,"y":0,"rotation_deg":0,"scale_x":1,"scale_y":1,"z":0,
            "ocular_yaw_deg":60,
        },
        "visual": {
            "fill_color":"#ffffff",
            "contour":{"color":"#000000","width":1,"opacity":1,"style":"solid","cap":"round","join":"round"},
            "material":{"name":"default","roughness":1,"metallic":0,"transmission":0,"emission":0},
            "opacity":1,"visibility":1,
        },
        "geometry": {
            "coordinate_frame":"component",
            "bounds":{"min_x":0,"min_y":0,"max_x":1,"max_y":1},
            "primitives":[],"paths":[],"surfaces":[],"masks":[],"anchors":{},"local_z":0,
        },
    }
    with pytest.raises(ValueError, match="conflicting legacy ocular parameter"):
        component_from_payload(
            "eye", "Eye", None,
            {"ocular_yaw_deg":{"value":30}}, {}, metadata,
        )
