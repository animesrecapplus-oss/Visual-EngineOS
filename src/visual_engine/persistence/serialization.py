from __future__ import annotations

from typing import Any

from visual_engine.components.common.meta import (
    Anchor, AppearanceLayer, Component, Constraint, ConstraintKind, Parameter, Profile, Relation, StateLayer,
)
from visual_engine.components.common.geometry_contract import (
    GeometryBounds, GeometryContract, GeometryMask, GeometryPath, GeometryPrimitive, GeometrySurface,
)
from visual_engine.components.common.visual_contract import (
    ContourContract, ContourOverride, LocalTransform, MaterialContract, MaterialOverride, VisualContract, VisualOverrides,
)
from visual_engine.components.common.base_color import (
    AlphaSemantics, BaseColor, BaseColorAuthoredRepresentation, BaseColorInheritance,
    BaseColorOverridePolicy, BaseColorProvenance, BaseColorRole, BaseColorSource, BaseColorSourceKind,
)
from visual_engine.components.common.palette import (
    Palette, PaletteEntry, PaletteSlot, PaletteSource, PaletteSourceKind,
    PaletteProvenance, PaletteInheritance, PaletteOverridePolicy, PaletteAuthoredRepresentation,
)


def _visual_payload(component: Component) -> dict[str, Any]:
    visual = component.visual
    contour = visual.contour
    material = visual.material
    return {
        "fill_color": visual.fill_color,
        "contour": {
            "color": contour.color, "width": contour.width, "opacity": contour.opacity,
            "style": contour.style, "cap": contour.cap, "join": contour.join,
        },
        "material": {
            "name": material.name, "roughness": material.roughness, "metallic": material.metallic,
            "transmission": material.transmission, "emission": material.emission,
        },
        "opacity": visual.opacity,
        "visibility": visual.visibility,
    }


def _override_payload(overrides: VisualOverrides | None) -> dict[str, Any] | None:
    if overrides is None:
        return None
    contour = overrides.contour
    material = overrides.material
    return {
        "fill_color": overrides.fill_color,
        "contour": None if contour is None else {
            "color": contour.color, "width": contour.width, "opacity": contour.opacity,
            "style": contour.style, "cap": contour.cap, "join": contour.join,
        },
        "material": None if material is None else {
            "name": material.name, "roughness": material.roughness, "metallic": material.metallic,
            "transmission": material.transmission, "emission": material.emission,
        },
        "opacity": overrides.opacity,
        "visibility": overrides.visibility,
    }


def _geometry_payload(geometry: GeometryContract) -> dict[str, Any]:
    return {
        "coordinate_frame": geometry.coordinate_frame,
        "bounds": {
            "min_x": geometry.bounds.min_x, "min_y": geometry.bounds.min_y,
            "max_x": geometry.bounds.max_x, "max_y": geometry.bounds.max_y,
        },
        "primitives": [{"kind": p.kind, "data": dict(p.data)} for p in geometry.primitives],
        "paths": [{"commands": [[cmd, list(values)] for cmd, values in p.commands]} for p in geometry.paths],
        "surfaces": [{"name": s.name, "data": dict(s.data)} for s in geometry.surfaces],
        "masks": [{"name": m.name, "operation": m.operation, "data": dict(m.data)} for m in geometry.masks],
        "anchors": {name: list(point) for name, point in sorted(geometry.anchors.items())},
        "local_z": geometry.local_z,
    }




def _base_color_payload(base_color: BaseColor | None) -> dict[str, Any] | None:
    if base_color is None:
        return None
    return {
        "canonical_color": {
            "red": base_color.canonical_color.red,
            "green": base_color.canonical_color.green,
            "blue": base_color.canonical_color.blue,
            "alpha": base_color.canonical_color.alpha,
        },
        "authored_representation": None if base_color.authored_representation is None else {
            "color_space": base_color.authored_representation.color_space,
            "value": base_color.authored_representation.value,
        },
        "source": {
            "kind": base_color.source.kind.value,
            "source_id": base_color.source.source_id,
            "component_id": base_color.source.component_id,
        },
        "provenance": {
            "target_component_id": base_color.provenance.target_component_id,
            "authority_component_id": base_color.provenance.authority_component_id,
            "source_id": base_color.provenance.source_id,
            "lineage": list(base_color.provenance.lineage),
            "rule": base_color.provenance.rule,
            "generator_id": base_color.provenance.generator_id,
            "generator_version": base_color.provenance.generator_version,
        },
        "role": base_color.role.value,
        "alpha_semantics": base_color.alpha_semantics.value,
        "inheritance": {
            "allow_children": base_color.inheritance.allow_children,
            "override_policy": base_color.inheritance.override_policy.value,
        },
        "fingerprint": base_color.fingerprint,
    }


def _base_color(payload: dict[str, Any] | None) -> BaseColor | None:
    if payload is None:
        return None
    from visual_engine.runtime.color_spaces import ColorRGBA
    canonical = payload["canonical_color"]
    base_color = BaseColor(
        canonical_color=ColorRGBA(canonical["red"], canonical["green"], canonical["blue"], canonical["alpha"]),
        authored_representation=None if payload["authored_representation"] is None else BaseColorAuthoredRepresentation(**payload["authored_representation"]),
        source=BaseColorSource(BaseColorSourceKind(payload["source"]["kind"]), payload["source"]["source_id"], payload["source"]["component_id"]),
        provenance=BaseColorProvenance(
            target_component_id=payload["provenance"]["target_component_id"],
            authority_component_id=payload["provenance"]["authority_component_id"],
            source_id=payload["provenance"]["source_id"],
            lineage=tuple(payload["provenance"]["lineage"]),
            rule=payload["provenance"]["rule"],
            generator_id=payload["provenance"]["generator_id"],
            generator_version=payload["provenance"]["generator_version"],
        ),
        role=BaseColorRole(payload["role"]),
        alpha_semantics=AlphaSemantics(payload["alpha_semantics"]),
        inheritance=BaseColorInheritance(
            allow_children=payload["inheritance"]["allow_children"],
            override_policy=BaseColorOverridePolicy(payload["inheritance"]["override_policy"]),
        ),
    )
    if base_color.fingerprint != payload.get("fingerprint"):
        raise ValueError("persisted BASE color fingerprint mismatch")
    return base_color



def _palette_payload(palette: Palette | None) -> dict[str, Any] | None:
    if palette is None:
        return None
    return {
        "entries": [
            {
                "slot": entry.slot.value,
                "canonical_color": {
                    "red": entry.canonical_color.red,
                    "green": entry.canonical_color.green,
                    "blue": entry.canonical_color.blue,
                    "alpha": entry.canonical_color.alpha,
                },
                "authored_representation": None if entry.authored_representation is None else {
                    "slot": entry.authored_representation.slot.value,
                    "value": entry.authored_representation.value,
                    "color_space": entry.authored_representation.color_space,
                },
            }
            for entry in palette.entries
        ],
        "source": {
            "kind": palette.source.kind.value,
            "source_id": palette.source.source_id,
            "component_id": palette.source.component_id,
        },
        "provenance": {
            "target_component_id": palette.provenance.target_component_id,
            "authority_component_id": palette.provenance.authority_component_id,
            "source_id": palette.provenance.source_id,
            "lineage": list(palette.provenance.lineage),
            "rule": palette.provenance.rule,
            "generator_id": palette.provenance.generator_id,
            "generator_version": palette.provenance.generator_version,
        },
        "inheritance": {
            "allow_children": palette.inheritance.allow_children,
            "override_policy": palette.inheritance.override_policy.value,
        },
        "fingerprint": palette.fingerprint,
    }


def _palette(payload: dict[str, Any] | None) -> Palette | None:
    if payload is None:
        return None
    from visual_engine.runtime.color_spaces import ColorRGBA
    entries = []
    for item in payload["entries"]:
        canonical = item["canonical_color"]
        authored = item.get("authored_representation")
        entries.append(PaletteEntry(
            slot=PaletteSlot(item["slot"]),
            canonical_color=ColorRGBA(canonical["red"], canonical["green"], canonical["blue"], canonical["alpha"]),
            authored_representation=None if authored is None else PaletteAuthoredRepresentation(
                slot=PaletteSlot(authored["slot"]), value=authored["value"], color_space=authored.get("color_space", "srgb")
            ),
        ))
    source = payload["source"]
    provenance = payload["provenance"]
    inheritance = payload["inheritance"]
    palette = Palette(
        entries=tuple(entries),
        source=PaletteSource(PaletteSourceKind(source["kind"]), source["source_id"], source["component_id"]),
        provenance=PaletteProvenance(
            target_component_id=provenance["target_component_id"],
            authority_component_id=provenance["authority_component_id"],
            source_id=provenance["source_id"],
            lineage=tuple(provenance["lineage"]),
            rule=provenance["rule"],
            generator_id=provenance.get("generator_id"),
            generator_version=provenance.get("generator_version"),
        ),
        inheritance=PaletteInheritance(
            allow_children=inheritance["allow_children"],
            override_policy=PaletteOverridePolicy(inheritance["override_policy"]),
        ),
    )
    if palette.fingerprint != payload.get("fingerprint"):
        raise ValueError("persisted palette fingerprint mismatch")
    return palette


def component_payload(component: Component, *, child_order: int | None = None) -> dict[str, Any]:
    """Serialize one component without embedding its children or relations.

    Relations are persisted in their own table so they remain queryable. Transform,
    visual and geometry contracts live in metadata because the relational schema does
    not pretend every future contract field is a fixed SQL column.
    """
    return {
        "transform": {
            "x": component.transform.x, "y": component.transform.y,
            "rotation_deg": component.transform.rotation_deg,
            "scale_x": component.transform.scale_x, "scale_y": component.transform.scale_y,
            "z": component.transform.z,
        },
        "visual": _visual_payload(component),
        "visual_overrides": _override_payload(component.visual_overrides),
        "base_color": _base_color_payload(component.base_color),
        "palette": _palette_payload(component.palette),
        "geometry": _geometry_payload(component.geometry),
        "persistence": {"child_order": child_order},
    }


def _visual(payload: dict[str, Any]) -> VisualContract:
    c = payload["contour"]
    m = payload["material"]
    return VisualContract(
        fill_color=payload["fill_color"],
        contour=ContourContract(**c),
        material=MaterialContract(**m),
        opacity=payload["opacity"], visibility=payload["visibility"],
    )


def _overrides(payload: dict[str, Any] | None) -> VisualOverrides | None:
    if payload is None:
        return None
    c = payload["contour"]
    m = payload["material"]
    return VisualOverrides(
        fill_color=payload["fill_color"],
        contour=None if c is None else ContourOverride(**c),
        material=None if m is None else MaterialOverride(**m),
        opacity=payload["opacity"], visibility=payload["visibility"],
    )


def _geometry(payload: dict[str, Any]) -> GeometryContract:
    b = payload["bounds"]
    return GeometryContract(
        coordinate_frame=payload["coordinate_frame"],
        bounds=GeometryBounds(**b),
        primitives=tuple(GeometryPrimitive(p["kind"], p["data"]) for p in payload["primitives"]),
        paths=tuple(GeometryPath(tuple((cmd, tuple(values)) for cmd, values in p["commands"])) for p in payload["paths"]),
        surfaces=tuple(GeometrySurface(s["name"], s["data"]) for s in payload["surfaces"]),
        masks=tuple(GeometryMask(m["name"], m["operation"], m["data"]) for m in payload["masks"]),
        anchors={name: tuple(point) for name, point in payload["anchors"].items()},
        local_z=payload["local_z"],
    )


def component_from_payload(
    component_id: str,
    kind: str,
    parent_id: str | None,
    parameters: dict[str, Any],
    anchors: dict[str, Any],
    metadata: dict[str, Any],
) -> Component:
    """Rehydrate a component from the relational projection plus contract metadata."""
    transform = dict(metadata["transform"])
    visual = metadata["visual"]
    geometry = metadata["geometry"]

    # V1.23 migration: V1.13–V1.22 stored ocular orientation inside the generic
    # LocalTransform. Move those legacy fields into the component parameter map
    # before constructing the now-generic transform. Conflicting persisted values
    # are rejected instead of silently choosing one source.
    legacy_ocular = {
        name: transform.pop(name)
        for name in ("alignment_axis_rotation_deg", "ocular_yaw_deg", "ocular_pitch_deg")
        if name in transform
    }
    parameters = dict(parameters)
    for name, value in legacy_ocular.items():
        existing = parameters.get(name)
        if existing is not None and float(existing["value"]) != float(value):
            raise ValueError(f"conflicting legacy ocular parameter: {name}")
        if existing is None:
            parameters[name] = {"value": value}

    component = Component(
        id=component_id,
        kind=kind,
        parent_id=parent_id,
        parameters={
            name: Parameter(name, item["value"], item.get("min_value"), item.get("max_value"))
            for name, item in parameters.items()
        },
        anchors={name: Anchor(name, item["x"], item["y"], item["z"]) for name, item in anchors.items()},
        transform=LocalTransform(**transform),
        visual=_visual(visual),
        visual_overrides=_overrides(metadata.get("visual_overrides")),
        base_color=_base_color(metadata.get("base_color")),
        palette=_palette(metadata.get("palette")),
        geometry=_geometry(geometry),
    )
    return component


def parameter_payload(parameters: dict[str, Parameter]) -> dict[str, Any]:
    return {
        name: {"value": p.value, "min_value": p.min_value, "max_value": p.max_value}
        for name, p in sorted(parameters.items())
    }
