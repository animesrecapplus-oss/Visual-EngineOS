from __future__ import annotations

import pytest

from visual_engine.components.common import BaseColor, BaseColorRole, Component, Palette, PaletteSlot
from visual_engine.persistence.serialization import component_from_payload, component_payload, parameter_payload


def test_palette_round_trip_preserves_fingerprint():
    c = Component(
        "object",
        "object",
        base_color=BaseColor.from_srgb("object", "#112233", role=BaseColorRole.PRIMARY),
        palette=Palette.from_srgb("object", {PaletteSlot.PRIMARY: "#AABBCC", PaletteSlot.ACCENT: "#DDEEFF"}),
    )
    payload = component_payload(c)
    restored = component_from_payload(c.id, c.kind, None, parameter_payload(c.parameters), {}, payload)
    assert restored.palette is not None
    assert restored.palette.fingerprint == c.palette.fingerprint
    assert restored.base_color.fingerprint == c.base_color.fingerprint


def test_tampered_palette_fingerprint_is_rejected():
    c = Component("object", "object", palette=Palette.from_srgb("object", {PaletteSlot.PRIMARY: "#AABBCC"}))
    payload = component_payload(c)
    payload["palette"]["fingerprint"] = "0" * 64
    with pytest.raises(ValueError, match="palette fingerprint mismatch"):
        component_from_payload(c.id, c.kind, None, parameter_payload(c.parameters), {}, payload)
