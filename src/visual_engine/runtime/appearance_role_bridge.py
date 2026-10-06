from __future__ import annotations

"""V1.28 renderer-neutral bridge from typed appearance composition to the legacy envelope.

The existing ``AppearanceResolutionInput.base_color`` field is retained for
backward compatibility.  V1.28 makes its ownership explicit: when an input is
built from an ``AppearanceComposition``, the field is derived from the selected
typed authority and a typed ``AppearanceRoleContribution`` travels beside it.
No color is mixed, premultiplied, shaded, or guessed here.
"""

from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING

from visual_engine.components.common.base_color import BaseColorRole
from visual_engine.runtime.appearance_composition import (
    AppearanceComposition,
    CompositionSource,
)
from visual_engine.runtime.color_spaces import ColorRGBA
from visual_engine.runtime.identity import stable_digest

if TYPE_CHECKING:  # pragma: no cover
    from visual_engine.runtime.appearance_contract import AppearanceResolutionInput


ROLE_BRIDGE_VERSION = "1"


class AppearanceRoleBridgeError(ValueError):
    """Raised when typed composition cannot safely cross the legacy boundary."""


class RoleContributionSource(str, Enum):
    BASE = "base"
    PALETTE = "palette"


@dataclass(frozen=True, slots=True)
class AppearanceRoleContribution:
    """Typed semantic color contribution carried into the renderer-neutral envelope.

    ``legacy_base_color`` is a compatibility representation only.  The canonical
    color remains the authoritative value; authored sRGB is preserved when the
    selected authority supplied it.  Provenance is copied rather than collapsed
    into a generic source string so downstream systems cannot lose lineage.
    """

    target_id: str
    role: BaseColorRole
    source: RoleContributionSource
    canonical_color: ColorRGBA
    authored_srgb: str | None
    authority_component_id: str
    source_id: str
    authority_fingerprint: str
    composition_fingerprint: str
    lineage: tuple[str, ...]
    legacy_base_color: str
    fingerprint: str

    def __post_init__(self) -> None:
        if not self.target_id or not self.authority_component_id or not self.source_id:
            raise AppearanceRoleBridgeError("role contribution identifiers are required")
        if not isinstance(self.role, BaseColorRole):
            raise AppearanceRoleBridgeError("role contribution role must be BaseColorRole")
        if not isinstance(self.source, RoleContributionSource):
            raise AppearanceRoleBridgeError("role contribution source is invalid")
        if not isinstance(self.canonical_color, ColorRGBA):
            raise AppearanceRoleBridgeError("role contribution canonical_color must be ColorRGBA")
        if not self.authority_fingerprint or len(self.authority_fingerprint) != 64:
            raise AppearanceRoleBridgeError("authority fingerprint must be SHA-256")
        if not self.composition_fingerprint or len(self.composition_fingerprint) != 64:
            raise AppearanceRoleBridgeError("composition fingerprint must be SHA-256")
        if not self.lineage or self.lineage[-1] != self.target_id:
            raise AppearanceRoleBridgeError("role contribution lineage must terminate at target")
        if len(set(self.lineage)) != len(self.lineage):
            raise AppearanceRoleBridgeError("role contribution lineage must not repeat IDs")
        if not isinstance(self.legacy_base_color, str) or len(self.legacy_base_color) not in (7, 9):
            raise AppearanceRoleBridgeError("legacy base_color must be #RRGGBB or #RRGGBBAA")
        if not self.legacy_base_color.startswith("#"):
            raise AppearanceRoleBridgeError("legacy base_color must be hexadecimal")
        try:
            int(self.legacy_base_color[1:], 16)
        except ValueError as exc:
            raise AppearanceRoleBridgeError("legacy base_color must be hexadecimal") from exc
        if self.authored_srgb is not None:
            if len(self.authored_srgb) not in (7, 9) or not self.authored_srgb.startswith("#"):
                raise AppearanceRoleBridgeError("authored_srgb must be #RRGGBB or #RRGGBBAA")
            if ColorRGBA.from_hex(self.authored_srgb) != self.canonical_color:
                raise AppearanceRoleBridgeError("authored_srgb contradicts canonical color")
            if self.legacy_base_color != self.authored_srgb:
                raise AppearanceRoleBridgeError("legacy base_color must preserve authored sRGB exactly")
        elif ColorRGBA.from_hex(self.legacy_base_color) != self.canonical_color:
            raise AppearanceRoleBridgeError("legacy base_color contradicts canonical color")
        expected = stable_digest({
            "version": ROLE_BRIDGE_VERSION,
            "target_id": self.target_id,
            "role": self.role,
            "source": self.source,
            "canonical_color": self.canonical_color,
            "authored_srgb": self.authored_srgb,
            "authority_component_id": self.authority_component_id,
            "source_id": self.source_id,
            "authority_fingerprint": self.authority_fingerprint,
            "composition_fingerprint": self.composition_fingerprint,
            "lineage": self.lineage,
            "legacy_base_color": self.legacy_base_color,
        })
        if self.fingerprint != expected:
            raise AppearanceRoleBridgeError("role contribution fingerprint mismatch")


def _selected_parts(composition: AppearanceComposition):
    if composition.status != "resolved":
        raise AppearanceRoleBridgeError(
            f"cannot bridge non-resolved composition: {composition.status}: {composition.reason}"
        )
    if composition.provenance.selected_source is CompositionSource.BASE:
        if composition.base_color is None:
            raise AppearanceRoleBridgeError("BASE-selected composition has no BASE authority")
        color = composition.base_color
        return (
            RoleContributionSource.BASE,
            color.canonical_color,
            None if color.authored_representation is None else color.authored_representation.value,
            color.provenance.authority_component_id,
            color.provenance.source_id,
            color.fingerprint,
            color.provenance.lineage,
        )
    if composition.provenance.selected_source is CompositionSource.PALETTE:
        if composition.palette_entry is None or composition.provenance.selected_slot is None:
            raise AppearanceRoleBridgeError("Palette-selected composition has no palette entry")
        entry = composition.palette_entry
        return (
            RoleContributionSource.PALETTE,
            entry.canonical_color,
            None if entry.authored_representation is None else entry.authored_representation.value,
            composition.provenance.palette_authority_component_id,
            composition.provenance.palette_source_id,
            composition.provenance.palette_fingerprint or entry.canonical_color.to_hex(),
            composition.provenance.palette_lineage,
        )
    raise AppearanceRoleBridgeError("composition selected no semantic source")


def bridge_appearance_composition(composition: AppearanceComposition) -> AppearanceRoleContribution:
    """Convert one resolved composition into a typed renderer-neutral role contribution."""
    source, canonical, authored, authority_id, source_id, authority_fp, lineage = _selected_parts(composition)
    if authority_id is None or source_id is None:
        raise AppearanceRoleBridgeError("selected composition is missing authority provenance")
    legacy = authored if authored is not None else canonical.to_hex()
    payload = {
        "target_id": composition.target_component_id,
        "role": composition.request.role,
        "source": source,
        "canonical_color": canonical,
        "authored_srgb": authored,
        "authority_component_id": authority_id,
        "source_id": source_id,
        "authority_fingerprint": authority_fp,
        "composition_fingerprint": composition.fingerprint,
        "lineage": tuple(lineage),
        "legacy_base_color": legacy,
    }
    fingerprint = stable_digest({"version": ROLE_BRIDGE_VERSION, **payload})
    return AppearanceRoleContribution(fingerprint=fingerprint, **payload)


def bridge_fingerprint(composition: AppearanceComposition) -> str:
    """Return the role-bridge identity without geometry or renderer state."""
    return bridge_appearance_composition(composition).fingerprint


def bridge_to_appearance_input(composition: AppearanceComposition, *, contour, material, opacity: float, visibility: float, active_states=(), appearance_layers=(), contributions=(), layer_resolution_digest: str = "") -> "AppearanceResolutionInput":
    """Build the legacy-compatible appearance input from one typed composition.

    Existing non-BASE contributions are preserved.  A second BASE contribution is
    rejected because that would create two authorities for the legacy field.
    """
    from visual_engine.runtime.appearance_contract import (
        AppearanceDomain,
        build_appearance_input,
    )

    role = bridge_appearance_composition(composition)
    if any(item.domain is AppearanceDomain.BASE for item in contributions):
        raise AppearanceRoleBridgeError(
            "cannot bridge a typed role while another BASE contribution is supplied"
        )
    return build_appearance_input(
        composition.target_component_id,
        base_color=role.legacy_base_color,
        contour=contour,
        material=material,
        opacity=opacity,
        visibility=visibility,
        active_states=tuple(active_states),
        appearance_layers=tuple(appearance_layers),
        contributions=tuple(contributions),
        layer_resolution_digest=layer_resolution_digest,
        role_contribution=role,
    )


def role_bridge_invalidation(graph, target_component_id: str, changed_component_id: str, request) -> tuple[bool, tuple[str, ...]]:
    """Report targeted invalidation causes for a role bridge.

    The bridge delegates dependency ownership to the existing BASE and Palette
    resolvers.  A sibling, geometry-only mutation, or an unused authority does
    not become a false dependency.  Composition modes further narrow which
    authority can affect the target.
    """
    from visual_engine.runtime.base_color_resolution import base_color_invalidation
    from visual_engine.runtime.palette_resolution import palette_invalidation
    from visual_engine.runtime.appearance_composition import CompositionMode

    reasons: list[str] = []
    if request.mode is not CompositionMode.PALETTE_ONLY:
        base_result = base_color_invalidation(graph, target_component_id, changed_component_id)
        base_affects, base_reason = base_result.affects_target, base_result.reason
        if base_affects:
            reasons.append(f"BASE: {base_reason}")
    if request.mode is not CompositionMode.BASE_ONLY:
        palette_affects, palette_reason = palette_invalidation(graph, target_component_id, changed_component_id)
        if palette_affects:
            reasons.append(f"PALETTE: {palette_reason}")
    return bool(reasons), tuple(reasons)
