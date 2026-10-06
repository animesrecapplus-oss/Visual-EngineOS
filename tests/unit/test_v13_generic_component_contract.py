from math import isclose
import math

import pytest

from visual_engine.model import (
    Component, ContourContract, LocalTransform, MaterialContract, Relation,
    VisualContract, contract_hash,
)
from visual_engine.runtime import RuntimeGraph, resolve_component_contract


def test_component_has_generic_visual_defaults():
    c = Component("x", "anything")
    assert c.visual.fill_color == "#ffffff"
    assert c.visual.contour.color == "#000000"
    assert c.visual.material.name == "default"
    assert c.visual.visibility == 1


def test_local_transform_composes_through_hierarchy():
    root = Component("root", "face", transform=LocalTransform(x=10, y=20, rotation_deg=30))
    child = Component("child", "eye", transform=LocalTransform(x=5, y=0, rotation_deg=15, z=2))
    root.add_child(child)
    resolved = resolve_component_contract(RuntimeGraph.from_component(root), "child")
    assert isclose(resolved.world_transform[0][2], 10 + 5 * 0.8660254037844386, rel_tol=1e-9)
    assert isclose(resolved.world_transform[1][2], 20 + 5 * 0.5, rel_tol=1e-9)
    assert isclose(resolved.world_z, 2.0)


def test_visibility_and_opacity_inherit_multiplicatively():
    root = Component("root", "face", visual=VisualContract(opacity=.8, visibility=.9))
    child = Component("child", "eye", visual=VisualContract(opacity=.5, visibility=.5))
    root.add_child(child)
    r = resolve_component_contract(RuntimeGraph.from_component(root), "child")
    assert isclose(r.visibility, .45)
    assert isclose(r.opacity, .4)
    assert isclose(r.effective_visibility, .18)


def test_shadow_changes_fill_and_contour_without_mutating_source_contract():
    v = VisualContract(fill_color="#ff0000", contour=ContourContract(color="#ffffff"))
    root = Component("x", "eye", visual=v)
    r = resolve_component_contract(RuntimeGraph.from_component(root), "x", shadow_alpha=.5)
    assert r.effective_fill_color == "#800000"
    assert r.effective_contour.color == "#808080"
    assert v.fill_color == "#ff0000"
    assert v.contour.color == "#ffffff"


def test_material_is_part_of_generic_contract():
    m = MaterialContract(name="glass", roughness=.1, transmission=.8)
    c = Component("glass", "object", visual=VisualContract(material=m))
    r = resolve_component_contract(RuntimeGraph.from_component(c), "glass")
    assert r.material == m


def test_occlusion_and_states_are_context_not_component_specific_logic():
    c = Component("eye", "ocular")
    r = resolve_component_contract(RuntimeGraph.from_component(c), "eye", occluded_by=("glasses",), active_states=("wet",))
    assert r.occluded_by == ("glasses",)
    assert r.active_states == ("wet",)


def test_contract_hash_is_deterministic_and_sensitive():
    a = VisualContract(fill_color="#ffffff")
    b = VisualContract(fill_color="#ffffff")
    c = VisualContract(fill_color="#eeeeee")
    t = LocalTransform()
    assert contract_hash(a, t) == contract_hash(b, t)
    assert contract_hash(a, t) != contract_hash(c, t)
    assert len(contract_hash(a, t)) == 64


def test_transform_rejects_zero_scale():
    with pytest.raises(ValueError):
        LocalTransform(scale_x=0)


def test_visual_overrides_inherit_unspecified_fields_and_override_explicit_fields():
    from visual_engine.model import VisualOverrides, ContourOverride, MaterialOverride
    root = Component(
        "root", "parent",
        visual=VisualContract(
            fill_color="#112233",
            contour=ContourContract(color="#445566", width=3),
            material=MaterialContract(name="metal", metallic=.8),
            opacity=.8,
            visibility=.9,
        ),
    )
    child = Component(
        "child", "child",
        visual_overrides=VisualOverrides(
            contour=ContourOverride(width=1),
            material=MaterialOverride(roughness=.2),
            opacity=.5,
        ),
    )
    root.add_child(child)
    r = __import__("visual_engine.runtime", fromlist=["resolve_component"]).resolve_component(
        RuntimeGraph.from_component(root), "child"
    )
    assert r.visual.effective_fill_color == "#112233"
    assert r.visual.effective_contour.color == "#445566"
    assert r.visual.effective_contour.width == 1
    assert r.visual.material.name == "metal"
    assert r.visual.material.metallic == .8
    assert r.visual.material.roughness == .2
    assert isclose(r.visual.opacity, .4)
    assert isclose(r.visual.visibility, .9)


def test_resolution_returns_generic_component_envelope_and_trace():
    from visual_engine.runtime import ResolutionContext, resolve_component
    root = Component("root", "parent")
    child = Component("child", "anything")
    root.add_child(child)
    r = resolve_component(
        RuntimeGraph.from_component(root),
        "child",
        context=ResolutionContext(active_states=("wet",)),
    )
    assert r.component_id == "child"
    assert r.kind == "anything"
    assert r.geometry == child.geometry
    assert r.visual.active_states == ("wet",)
    assert "child.visual=explicit-legacy" in r.trace.entries


def test_transform_identity_and_negative_scale_are_deterministic():
    identity = LocalTransform().matrix()
    assert identity == ((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))
    mirrored = LocalTransform(scale_x=-1, scale_y=1).matrix()
    assert mirrored[0][0] == -1.0
    assert mirrored[1][1] == 1.0


def test_full_turn_preserves_translation_and_scale_with_tolerance():
    t = LocalTransform(x=7, y=-3, rotation_deg=360, scale_x=2, scale_y=3)
    m = t.matrix()
    assert isclose(m[0][0], 2.0, abs_tol=1e-12)
    assert isclose(m[1][1], 3.0, abs_tol=1e-12)
    assert isclose(m[0][1], 0.0, abs_tol=1e-12)
    assert isclose(m[1][0], 0.0, abs_tol=1e-12)
    assert m[0][2] == 7.0
    assert m[1][2] == -3.0


def test_deep_transform_chain_is_stable():
    root = Component("root", "x", transform=LocalTransform(x=1, y=2, rotation_deg=10))
    current = root
    for i in range(1, 20):
        child = Component(f"c{i}", "x", transform=LocalTransform(x=.1, y=.2, rotation_deg=1, scale_x=1.001, scale_y=.999))
        current.add_child(child)
        current = child
    r = __import__("visual_engine.runtime", fromlist=["resolve_component"]).resolve_component(
        RuntimeGraph.from_component(root), "c19"
    )
    assert all(math.isfinite(v) for row in r.visual.world_transform for v in row)


def test_contract_and_geometry_hashes_are_cross_process_stable(tmp_path):
    import subprocess
    import sys
    code = """
from visual_engine.model import VisualContract, GeometryContract, GeometryPrimitive, LocalTransform, contract_hash, geometry_hash
v = VisualContract(fill_color='#123456')
g = GeometryContract(primitives=(GeometryPrimitive('circle', {'r': 2}),))
print(contract_hash(v, LocalTransform(x=2, rotation_deg=15)))
print(geometry_hash(g))
"""
    env = dict(__import__("os").environ)
    env["PYTHONPATH"] = "src"
    outputs = []
    for _ in range(2):
        result = subprocess.run([sys.executable, "-c", code], cwd=__import__("pathlib").Path(__file__).resolve().parents[2], env=env, capture_output=True, text=True, check=True)
        outputs.append(result.stdout.strip())
    assert outputs[0] == outputs[1]
