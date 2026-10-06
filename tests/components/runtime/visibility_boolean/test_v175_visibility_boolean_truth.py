from __future__ import annotations

from pathlib import Path

import pytest

from visual_engine.components.common.geometry_contract import GeometryContract, GeometryPrimitive
from visual_engine.runtime import BooleanOperation as public_operation
from visual_engine.runtime import boolean_operation as public_boolean_operation
from visual_engine.runtime.visibility import BooleanOperation as legacy_operation
from visual_engine.runtime.visibility_boolean import (
    BooleanOperation,
    difference_geometry,
    intersection_geometry,
    union_geometries,
)

ROOT = Path(__file__).parents[4]


def rect(x0: float, y0: float, x1: float, y1: float) -> GeometryContract:
    return GeometryContract(
        primitives=(GeometryPrimitive("polygon", {"points": ((x0, y0), (x1, y0), (x1, y1), (x0, y1))}),),
    )


def test_canonical_owner_preserves_public_and_legacy_identity() -> None:
    assert public_operation is BooleanOperation
    assert legacy_operation is BooleanOperation
    assert public_boolean_operation.__module__ == "visual_engine.runtime.visibility_boolean"
    assert (ROOT / "src/visual_engine/runtime/visibility_boolean.py").exists()


def test_boolean_contract_is_frozen_and_deterministic() -> None:
    first = public_boolean_operation(rect(0, 0, 8, 8), rect(4, 2, 12, 6), BooleanOperation.INTERSECTION)
    second = public_boolean_operation(rect(0, 0, 8, 8), rect(4, 2, 12, 6), BooleanOperation.INTERSECTION)
    assert first == second
    with pytest.raises((AttributeError, TypeError)):
        first.area = 1.0


def test_union_intersection_difference_preserve_geometry_contract() -> None:
    a, b = rect(0, 0, 10, 10), rect(3, 3, 7, 7)
    assert union_geometries((a, b)).area == pytest.approx(100.0)
    assert intersection_geometry(a, b).area == pytest.approx(16.0)
    difference = difference_geometry(a, b)
    assert difference.area == pytest.approx(84.0)
    assert len(difference.polygons) == 1
    assert len(difference.polygons[0].holes) == 1


def test_empty_union_and_disjoint_intersection_are_closed_results() -> None:
    assert union_geometries(()).area == 0.0
    assert intersection_geometry(rect(0, 0, 1, 1), rect(2, 2, 3, 3)).area == 0.0


def test_hostile_invalid_geometry_and_operation_fail_closed() -> None:
    invalid = GeometryContract(primitives=(GeometryPrimitive("ellipse", {"cx": 0, "cy": 0, "rx": -1, "ry": 1}),))
    with pytest.raises(ValueError, match="non-negative|negative"):
        public_boolean_operation(invalid, rect(0, 0, 1, 1), BooleanOperation.UNION)
    with pytest.raises(ValueError, match="unsupported boolean operation"):
        public_boolean_operation(rect(0, 0, 1, 1), rect(0, 0, 1, 1), "invalid")  # type: ignore[arg-type]


def test_visibility_module_no_longer_owns_boolean_implementations() -> None:
    source = (ROOT / "src/visual_engine/runtime/visibility.py").read_text(encoding="utf-8")
    assert "class BooleanOperation" not in source
    assert "def boolean_operation(" not in source
    assert "def union_geometries(" not in source
    assert "def intersection_geometry(" not in source
    assert "def difference_geometry(" not in source
    assert "inter = target.intersection(occ)" in source
    assert "so.unary_union(intersections)" in source
