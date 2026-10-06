from pathlib import Path

from tools.audit_v143_first_production_consumer import ROOT, scan


def test_v143_historical_boundary_is_now_superseded_by_v145_owner_v161_style_owner_and_v167_render_owner():
    result = scan()
    assert result["external_resolver_call_sites"]
    assert {item["path"] for item in result["external_resolver_call_sites"]} == {
        "src/visual_engine/runtime/production_face_render.py",
        "src/visual_engine/runtime/production_visual_styles.py",
    }
    assert result["decision"] == "CONSUMER_FOUND_REVIEW_REQUIRED"


def test_v145_is_the_only_current_production_resolution_cache_owner():
    result = scan()
    owners = result["external_resolution_cache_instantiations"]
    assert owners
    assert {item["path"] for item in owners} == {"src/visual_engine/runtime/production_render_session.py"}


def test_runtime_scene_dependency_is_data_only_and_scene_does_not_inject_runtime():
    result = scan()
    # Geometry/region transforms consume Frame/Camera/Placement data, but the
    # scene package does not own or invoke generic component resolution.
    assert result["runtime_scene_imports"] == []


def test_scene_does_not_inject_generic_resolution_runtime():
    result = scan()
    assert result["runtime_scene_imports"] == []


def test_geometry_cache_has_a_distinct_real_graph_api():
    source = (ROOT / "src/visual_engine/runtime/geometry_cache.py").read_text(encoding="utf-8")
    assert "def get_or_build_for_graph(" in source
    contract = (ROOT / "src/visual_engine/runtime/contract.py").read_text(encoding="utf-8")
    assert "def resolve_component(" in contract


def test_runtime_graph_is_built_by_persistence_but_not_resolved_there():
    source = (ROOT / "src/visual_engine/persistence/postgres.py").read_text(encoding="utf-8")
    assert "RuntimeGraph.from_component(root)" in source
    assert "resolve_component(" not in source
