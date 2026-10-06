from __future__ import annotations

from dataclasses import FrozenInstanceError

import pytest

from visual_engine.runtime import ProductionRenderResult as PublicResult
from visual_engine.runtime.production_face_render import ProductionRenderResult as ProducerResult
from visual_engine.runtime.production_render_result import ProductionRenderResult
from visual_engine.runtime.production_slice import ProductionRenderResult as CompatibilityResult


def test_canonical_public_producer_and_compatibility_identity() -> None:
    assert PublicResult is ProductionRenderResult
    assert ProducerResult is ProductionRenderResult
    assert CompatibilityResult is ProductionRenderResult
    assert ProductionRenderResult.__module__ == "visual_engine.runtime.production_render_result"


def test_result_is_frozen_and_slot_based() -> None:
    fields = {field.name for field in ProductionRenderResult.__dataclass_fields__.values()}
    assert fields == {
        "component_id", "generator", "resolution", "geometry", "camera_geometry",
        "svg", "visibility", "hair_ear_occlusion", "head_ear_occlusion",
    }
    assert hasattr(ProductionRenderResult, "__slots__")
    result = ProductionRenderResult("face", "generator", None, None, None, "<svg")
    with pytest.raises(FrozenInstanceError):
        result.component_id = "other"
    with pytest.raises((AttributeError, TypeError)):
        result.extra = object()


def test_result_owner_does_not_reconstruct_render_semantics() -> None:
    module = ProductionRenderResult.__module__
    assert module == "visual_engine.runtime.production_render_result"
    assert ProductionRenderResult.__annotations__["svg"] == "str"
