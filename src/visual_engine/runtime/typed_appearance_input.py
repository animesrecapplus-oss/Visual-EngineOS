from __future__ import annotations

"""V1.29 canonical typed appearance input envelope.

This module is the renderer-neutral hand-off between role composition and domain
resolution.  The selected ``AppearanceRoleContribution`` is authoritative for
BASE/COLOR entry semantics; the legacy hexadecimal field is derived only at the
compatibility boundary.  Geometry and transform data are intentionally absent.
"""

from dataclasses import dataclass

from visual_engine.components.common.meta import AppearanceLayer
from visual_engine.components.common.visual_contract import ContourContract, MaterialContract
from visual_engine.runtime.appearance_contract import AppearanceContribution, AppearanceDomain
from visual_engine.runtime.appearance_role_bridge import AppearanceRoleContribution, bridge_appearance_composition
from visual_engine.runtime.appearance_composition import AppearanceComposition
from visual_engine.runtime.identity import stable_digest


TYPED_APPEARANCE_INPUT_VERSION = "1"


class TypedAppearanceInputError(ValueError):
    """Raised when the canonical typed appearance envelope is contradictory."""


@dataclass(frozen=True, slots=True)
class TypedAppearanceInput:
    """Canonical appearance input for one target and one selected semantic role."""

    target_id: str
    role_contribution: AppearanceRoleContribution
    contour: ContourContract
    material: MaterialContract
    opacity: float
    visibility: float
    active_states: tuple[str, ...] = ()
    appearance_layers: tuple[AppearanceLayer, ...] = ()
    contributions: tuple[AppearanceContribution, ...] = ()
    layer_resolution_digest: str = ""
    fingerprint: str = ""

    def __post_init__(self) -> None:
        if not self.target_id:
            raise TypedAppearanceInputError("typed appearance target_id must not be empty")
        if not isinstance(self.role_contribution, AppearanceRoleContribution):
            raise TypedAppearanceInputError("typed appearance requires an AppearanceRoleContribution")
        if self.role_contribution.target_id != self.target_id:
            raise TypedAppearanceInputError("role contribution target does not match typed appearance target")
        if not 0.0 <= self.opacity <= 1.0 or not 0.0 <= self.visibility <= 1.0:
            raise TypedAppearanceInputError("typed appearance opacity/visibility must be in [0,1]")
        if tuple(sorted(set(self.active_states))) != self.active_states:
            raise TypedAppearanceInputError("active_states must be canonicalized")
        if any(not isinstance(layer, AppearanceLayer) for layer in self.appearance_layers):
            raise TypedAppearanceInputError("appearance_layers must contain AppearanceLayer instances")
        if any(not isinstance(item, AppearanceContribution) for item in self.contributions):
            raise TypedAppearanceInputError("contributions must contain AppearanceContribution instances")
        if any(item.domain is AppearanceDomain.BASE for item in self.contributions):
            raise TypedAppearanceInputError(
                "typed role input cannot carry a second BASE contribution"
            )
        if self.layer_resolution_digest and (
            len(self.layer_resolution_digest) != 64
            or any(c not in "0123456789abcdef" for c in self.layer_resolution_digest.lower())
        ):
            raise TypedAppearanceInputError("layer_resolution_digest must be a SHA-256 hexadecimal digest")
        ids = [item.contribution_id for item in self.contributions]
        if len(ids) != len(set(ids)):
            raise TypedAppearanceInputError("appearance contribution IDs must be unique")
        expected = stable_digest({
            "version": TYPED_APPEARANCE_INPUT_VERSION,
            "target_id": self.target_id,
            "role_contribution": self.role_contribution.fingerprint,
            "contour": self.contour,
            "material": self.material,
            "opacity": self.opacity,
            "visibility": self.visibility,
            "active_states": self.active_states,
            "appearance_layers": self.appearance_layers,
            "contributions": self.contributions,
            "layer_resolution_digest": self.layer_resolution_digest,
        })
        if self.fingerprint != expected:
            raise TypedAppearanceInputError("typed appearance input fingerprint mismatch")

    @property
    def legacy_base_color(self) -> str:
        """Derived compatibility representation; never an independent authority."""
        return self.role_contribution.legacy_base_color

    @classmethod
    def from_composition(
        cls,
        composition: AppearanceComposition,
        *,
        contour: ContourContract,
        material: MaterialContract,
        opacity: float,
        visibility: float,
        active_states: tuple[str, ...] = (),
        appearance_layers: tuple[AppearanceLayer, ...] = (),
        contributions: tuple[AppearanceContribution, ...] = (),
        layer_resolution_digest: str = "",
    ) -> "TypedAppearanceInput":
        role = bridge_appearance_composition(composition)
        canonical_states = tuple(sorted(set(active_states)))
        ids = [item.contribution_id for item in contributions]
        if len(ids) != len(set(ids)):
            raise TypedAppearanceInputError("appearance contribution IDs must be unique")
        payload = {
            "version": TYPED_APPEARANCE_INPUT_VERSION,
            "target_id": composition.target_component_id,
            "role_contribution": role.fingerprint,
            "contour": contour,
            "material": material,
            "opacity": opacity,
            "visibility": visibility,
            "active_states": canonical_states,
            "appearance_layers": tuple(appearance_layers),
            "contributions": tuple(contributions),
            "layer_resolution_digest": layer_resolution_digest,
        }
        return cls(
            target_id=composition.target_component_id,
            role_contribution=role,
            contour=contour,
            material=material,
            opacity=opacity,
            visibility=visibility,
            active_states=canonical_states,
            appearance_layers=tuple(appearance_layers),
            contributions=tuple(contributions),
            layer_resolution_digest=layer_resolution_digest,
            fingerprint=stable_digest(payload),
        )

    def to_base_domain_input(self, *, dependencies=()):
        """Create the BASE domain envelope without passing through the legacy API.

        This is the V1.30 migration seam: domain consumers receive the typed
        role directly, while the legacy hexadecimal representation remains
        available only to compatibility callers.
        """
        from visual_engine.runtime.base_resolution import build_base_resolution_input_from_typed

        return build_base_resolution_input_from_typed(self, dependencies=dependencies)

    def to_color_domain_input(self, *, dependencies=()):
        """Project only the selected semantic role into the typed COLOR domain.

        The projection deliberately excludes contour, material, opacity, state,
        layers and other appearance payloads so COLOR identity cannot accidentally
        inherit dependencies owned by another domain.
        """
        from visual_engine.runtime.color_resolution import TypedColorInput

        return TypedColorInput.from_typed_appearance_input(self).to_domain_input(
            dependencies=dependencies
        )

    def as_legacy_appearance_input(self):
        """Enter the pre-V1.29 API using only the typed value as its source.

        This method intentionally remains the *only* typed-to-legacy escape
        hatch. Production domain consumers must not use it.
        """
        from visual_engine.runtime.appearance_contract import build_appearance_input

        return build_appearance_input(
            self.target_id,
            base_color=self.legacy_base_color,
            contour=self.contour,
            material=self.material,
            opacity=self.opacity,
            visibility=self.visibility,
            active_states=self.active_states,
            appearance_layers=self.appearance_layers,
            contributions=self.contributions,
            layer_resolution_digest=self.layer_resolution_digest,
            role_contribution=self.role_contribution,
        )
