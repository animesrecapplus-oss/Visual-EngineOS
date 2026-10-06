from __future__ import annotations

from pathlib import Path

import pytest

from visual_engine.components.common.geometry_contract import GeometryBounds, GeometryContract, GeometryPrimitive
from visual_engine.runtime import CoverageIntent as public_coverage
from visual_engine.runtime.placement import CoverageIntent as legacy_coverage
from visual_engine.runtime.placement_coverage import CoverageIntent, resolve_coverage_scale
from visual_engine.runtime.region_geometry import geometry_to_region

ROOT = Path(__file__).parents[4]


def rect(x0: float, y0: float, x1: float, y1: float, anchor: tuple[float, float, float]) -> GeometryContract:
    return GeometryContract(
        bounds=GeometryBounds(x0, y0, x1, y1),
        primitives=(GeometryPrimitive("polygon", {"points": ((x0, y0), (x1, y0), (x1, y1), (x0, y1))}),),
        anchors={"anchor": anchor},
    )


def test_canonical_owner_and_legacy_identity_are_singleton() -> None:
    # The package and historical placement paths must expose the same contract object.
    assert public_coverage is CoverageIntent
    assert legacy_coverage is CoverageIntent
    assert (ROOT / "src/visual_engine/runtime/placement_coverage.py").exists()


def test_contract_is_frozen_and_rejects_non_finite_or_invalid_limits() -> None:
    intent = CoverageIntent(0.25)
    with pytest.raises((AttributeError, TypeError)):
        intent.target_fraction = 0.5
    with pytest.raises(ValueError, match=r"\[0,1\]"):
        CoverageIntent(float("nan"))
    with pytest.raises(ValueError, match=r"\[0,1\]"):
        CoverageIntent(float("inf"))
    with pytest.raises(ValueError, match="tolerance"):
        CoverageIntent(0.25, tolerance=0.0)
    with pytest.raises(ValueError, match="max_iterations"):
        CoverageIntent(0.25, max_iterations=7)


def test_solver_preserves_anchor_coverage_contract() -> None:
    source = rect(0, 0, 2, 2, (1, 1, 0))
    target = rect(0, 0, 4, 4, (2, 2, 0))
    scale, fraction, iterations = resolve_coverage_scale(
        geometry_to_region(source), geometry_to_region(target),
        source.anchors["anchor"], target.anchors["anchor"],
        CoverageIntent(0.25, tolerance=1e-5), 0.0, 0.0, 0.0,
    )
    assert scale == pytest.approx(1.0, rel=1e-4)
    assert fraction == pytest.approx(0.25, abs=1e-5)
    assert iterations > 0


def test_solver_rejects_invalid_regions_and_outside_anchors() -> None:
    source = rect(0, 0, 2, 2, (10, 10, 0))
    target = rect(0, 0, 4, 4, (2, 2, 0))
    with pytest.raises(ValueError, match="source_anchor"):
        resolve_coverage_scale(
            geometry_to_region(source), geometry_to_region(target),
            source.anchors["anchor"], target.anchors["anchor"],
            CoverageIntent(0.25), 0.0, 0.0, 0.0,
        )


def test_solver_rejects_non_finite_numeric_transform_inputs() -> None:
    source = rect(0, 0, 2, 2, (1, 1, 0))
    target = rect(0, 0, 4, 4, (2, 2, 0))
    with pytest.raises((ValueError, TypeError)):
        resolve_coverage_scale(
            geometry_to_region(source), geometry_to_region(target),
            source.anchors["anchor"], target.anchors["anchor"],
            CoverageIntent(0.25), float("nan"), 0.0, 0.0,
        )


def test_placement_module_no_longer_owns_coverage_solver() -> None:
    source = (ROOT / "src/visual_engine/runtime/placement.py").read_text(encoding="utf-8")
    assert "class CoverageIntent" not in source
    assert "def _solve_coverage_scale" not in source
    assert "from visual_engine.runtime.placement_coverage import CoverageIntent, resolve_coverage_scale" in source
    relation_source = (ROOT / "src/visual_engine/runtime/spatial_relationships.py").read_text(encoding="utf-8")
    assert "from visual_engine.runtime.placement_coverage import CoverageIntent" in relation_source


def test_solver_rejects_bad_types_zero_area_and_unreachable_requests() -> None:
    source = rect(0, 0, 2, 2, (1, 1, 0))
    target = rect(0, 0, 4, 4, (2, 2, 0))
    regions = geometry_to_region(source), geometry_to_region(target)
    with pytest.raises(TypeError, match="CoverageIntent"):
        resolve_coverage_scale(*regions, source.anchors["anchor"], target.anchors["anchor"], 0.25, 0.0, 0.0, 0.0)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="finite x/y/z"):
        resolve_coverage_scale(*regions, (1.0, 1.0, float("inf")), target.anchors["anchor"], CoverageIntent(0.25), 0.0, 0.0, 0.0)
    with pytest.raises(ValueError, match="unreachable"):
        resolve_coverage_scale(*regions, source.anchors["anchor"], target.anchors["anchor"], CoverageIntent(0.99, tolerance=1e-9), 180.0, 1e9, 1e9)


def test_zero_coverage_and_boundary_anchor_remain_deterministic() -> None:
    source = rect(0, 0, 2, 2, (0, 1, 0))
    target = rect(0, 0, 4, 4, (0, 2, 0))
    result = resolve_coverage_scale(
        geometry_to_region(source), geometry_to_region(target),
        source.anchors["anchor"], target.anchors["anchor"],
        CoverageIntent(0.0), 0.0, 0.0, 0.0,
    )
    assert result[0] == 1e-9
    assert result[1] == pytest.approx(0.0, abs=1e-12)
    assert result[2] == 0
