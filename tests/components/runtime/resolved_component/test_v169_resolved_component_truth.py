from __future__ import annotations

import importlib
from dataclasses import FrozenInstanceError

import pytest

from visual_engine.components.common.geometry_contract import GeometryContract
from visual_engine.components.common.visual_contract import ContourContract, MaterialContract, ResolvedVisualContract
from visual_engine.runtime import ResolutionTrace as PublicTrace
from visual_engine.runtime import ResolvedComponent as PublicResult
from visual_engine.runtime.contract import ResolutionTrace as CompatibilityTrace
from visual_engine.runtime.contract import ResolvedComponent as CompatibilityResult
from visual_engine.runtime.provenance import ResolutionProvenance
from visual_engine.runtime.resolved_component import ResolutionTrace, ResolvedComponent
from visual_engine.runtime.versioning import VersionStamp


def _result() -> ResolvedComponent:
    return ResolvedComponent(
        component_id="face",
        kind="face",
        visual=ResolvedVisualContract(
            world_transform=((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0)),
            world_z=0.0,
            visibility=1.0,
            opacity=1.0,
            effective_fill_color="#ffffff",
            effective_contour=ContourContract(),
            material=MaterialContract(),
        ),
        geometry=GeometryContract(),
        trace=ResolutionTrace(("face.visual=explicit-root",)),
        provenance=ResolutionProvenance(),
        version=VersionStamp(),
    )


def test_canonical_owner_and_compatibility_identity() -> None:
    assert PublicResult is ResolvedComponent
    assert CompatibilityResult is ResolvedComponent
    assert PublicTrace is ResolutionTrace
    assert CompatibilityTrace is ResolutionTrace
    assert ResolvedComponent.__module__ == "visual_engine.runtime.resolved_component"


def test_result_is_frozen_slots_and_value_preserving() -> None:
    result = _result()
    assert result.component_id == "face"
    assert result.trace.entries == ("face.visual=explicit-root",)
    assert hasattr(result, "__slots__")
    with pytest.raises(FrozenInstanceError):
        result.component_id = "other"  # type: ignore[misc]
    with pytest.raises((AttributeError, TypeError)):
        result.extra = object()  # type: ignore[attr-defined]


def test_trace_is_frozen_and_deterministic() -> None:
    first = ResolutionTrace(("a", "b"))
    second = ResolutionTrace(("a", "b"))
    assert first == second
    with pytest.raises(FrozenInstanceError):
        first.entries = ("changed",)  # type: ignore[misc]


def test_owner_has_no_legacy_facade_dependency() -> None:
    module = importlib.import_module("visual_engine.runtime.resolved_component")
    assert not any(
        getattr(value, "__module__", "") == "visual_engine.runtime.contract"
        for value in module.__dict__.values()
        if value is not ResolutionTrace and value is not ResolvedComponent
    )
