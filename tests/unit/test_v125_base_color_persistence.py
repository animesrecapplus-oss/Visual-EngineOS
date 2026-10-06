from visual_engine.components.common import BaseColor, BaseColorInheritance, BaseColorOverridePolicy, Component
from visual_engine.persistence.serialization import component_from_payload, component_payload


def test_typed_base_color_round_trips_through_component_metadata():
    color = BaseColor.from_srgb(
        "object",
        "#AaBbCc80",
        source_id="author:object:base",
        inheritance=BaseColorInheritance(override_policy=BaseColorOverridePolicy.REJECT_CONFLICT),
    )
    component = Component("object", "object", base_color=color)
    payload = component_payload(component)
    assert payload["base_color"]["authored_representation"]["value"] == "#AaBbCc80"
    assert payload["base_color"]["fingerprint"] == color.fingerprint

    restored = component_from_payload("object", "object", None, {}, {}, payload)
    assert restored.base_color == color
    assert restored.base_color.fingerprint == color.fingerprint


def test_persisted_base_color_fingerprint_tampering_is_rejected():
    color = BaseColor.from_srgb("object", "#123456")
    payload = component_payload(Component("object", "object", base_color=color))
    payload["base_color"]["fingerprint"] = "0" * 64
    try:
        component_from_payload("object", "object", None, {}, {}, payload)
    except ValueError as exc:
        assert "fingerprint mismatch" in str(exc)
    else:
        raise AssertionError("tampered BASE fingerprint must be rejected")


def test_old_payload_without_typed_base_color_remains_loadable():
    component = component_from_payload(
        "legacy",
        "object",
        None,
        {},
        {},
        {
            "transform": {"x": 0, "y": 0, "rotation_deg": 0, "scale_x": 1, "scale_y": 1, "z": 0},
            "visual": {
                "fill_color": "#ffffff",
                "contour": {"color": "#000000", "width": 1, "opacity": 1, "style": "solid", "cap": "round", "join": "round"},
                "material": {"name": "default", "roughness": 1, "metallic": 0, "transmission": 0, "emission": 0},
                "opacity": 1,
                "visibility": 1,
            },
            "visual_overrides": None,
            "geometry": {
                "coordinate_frame": "local",
                "bounds": {"min_x": 0, "min_y": 0, "max_x": 0, "max_y": 0},
                "primitives": [], "paths": [], "surfaces": [], "masks": [], "anchors": {}, "local_z": 0,
            },
        },
    )
    assert component.base_color is None
