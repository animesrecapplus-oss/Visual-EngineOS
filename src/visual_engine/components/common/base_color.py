from __future__ import annotations

"""Typed BASE appearance value objects.

V1.25 gives BASE color a closed, renderer-neutral contract.  The object stores
both the authored sRGB representation and the canonical linear-sRGB value so
future resolvers never have to guess whether a hexadecimal value was already
linearized.  No compositing, palette generation, lighting, or material shading
belongs here.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover - imports used only by static analyzers
    from visual_engine.runtime.color_spaces import ColorRGBA


class BaseColorError(ValueError):
    """Raised when a typed BASE color violates its contract."""


class BaseColorSourceKind(str, Enum):
    AUTHORED = "authored"
    INHERITED = "inherited"
    GENERATED = "generated"


class BaseColorRole(str, Enum):
    """Semantic color slot; deliberately independent from material/lighting."""

    PRIMARY = "primary"
    SECONDARY = "secondary"
    ACCENT = "accent"
    DETAIL = "detail"
    BACKGROUND = "background"
    CUSTOM = "custom"


class AlphaSemantics(str, Enum):
    """How BASE alpha is represented at this boundary.

    UNASSOCIATED means alpha travels beside RGB and is never premultiplied or
    composited here.  OPAQUE is the explicit alpha=1 case.
    """

    OPAQUE = "opaque"
    UNASSOCIATED = "unassociated"


class BaseColorOverridePolicy(str, Enum):
    LOCAL_WINS = "local-wins"
    INHERIT_WINS = "inherit-wins"
    REJECT_CONFLICT = "reject-conflict"


@dataclass(frozen=True, slots=True)
class BaseColorInheritance:
    """Explicit inheritance policy attached to one BASE authority."""

    allow_children: bool = True
    override_policy: BaseColorOverridePolicy = BaseColorOverridePolicy.LOCAL_WINS

    def __post_init__(self) -> None:
        if not isinstance(self.allow_children, bool):
            raise BaseColorError("BaseColorInheritance.allow_children must be boolean")
        if not isinstance(self.override_policy, BaseColorOverridePolicy):
            raise BaseColorError("unsupported BASE override policy")


@dataclass(frozen=True, slots=True)
class BaseColorAuthoredRepresentation:
    """Exact source representation retained alongside canonical color."""

    color_space: str
    value: str

    def __post_init__(self) -> None:
        if self.color_space != "srgb":
            raise BaseColorError("V1.25 authored BASE representation must be sRGB")
        if not isinstance(self.value, str) or len(self.value) not in (7, 9) or not self.value.startswith("#"):
            raise BaseColorError("authored sRGB value must be #RRGGBB or #RRGGBBAA")
        try:
            int(self.value[1:], 16)
        except ValueError as exc:
            raise BaseColorError("authored sRGB value must be hexadecimal") from exc


@dataclass(frozen=True, slots=True)
class BaseColorSource:
    """Identity of the authority that supplied this BASE value."""

    kind: BaseColorSourceKind
    source_id: str
    component_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, BaseColorSourceKind):
            raise BaseColorError("BaseColorSource.kind must be a BaseColorSourceKind")
        if not self.source_id or not self.component_id:
            raise BaseColorError("BASE source_id and component_id are required")


@dataclass(frozen=True, slots=True)
class BaseColorProvenance:
    """Deterministic lineage for an authored, inherited, or generated BASE."""

    target_component_id: str
    authority_component_id: str
    source_id: str
    lineage: tuple[str, ...] = ()
    rule: str = "local-authority"
    generator_id: str | None = None
    generator_version: str | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("target_component_id", self.target_component_id),
            ("authority_component_id", self.authority_component_id),
            ("source_id", self.source_id),
            ("rule", self.rule),
        ):
            if not isinstance(value, str) or not value:
                raise BaseColorError(f"BASE provenance {name} must be non-empty")
        if any(not isinstance(item, str) or not item for item in self.lineage):
            raise BaseColorError("BASE provenance lineage entries must be non-empty strings")
        if len(set(self.lineage)) != len(self.lineage):
            raise BaseColorError("BASE provenance lineage must not repeat component IDs")
        if (self.generator_id is None) != (self.generator_version is None):
            raise BaseColorError("generator_id and generator_version must be provided together")
        if self.generator_id is not None and not self.generator_id:
            raise BaseColorError("generator_id must be non-empty")
        if self.generator_version is not None and not self.generator_version:
            raise BaseColorError("generator_version must be non-empty")


@dataclass(frozen=True, slots=True)
class BaseColor:
    """One authoritative BASE color for one component.

    ``canonical_color`` is always linear-sRGB RGBA.  ``authored_representation``
    preserves the exact input spelling, including case and optional alpha bytes.
    The fingerprint is content-only and contains no geometry/transform data.
    """

    canonical_color: "ColorRGBA"
    authored_representation: BaseColorAuthoredRepresentation | None
    source: BaseColorSource
    provenance: BaseColorProvenance
    role: BaseColorRole = BaseColorRole.PRIMARY
    alpha_semantics: AlphaSemantics = AlphaSemantics.OPAQUE
    inheritance: BaseColorInheritance = field(default_factory=BaseColorInheritance)
    fingerprint: str = field(init=False)

    def __post_init__(self) -> None:
        from visual_engine.runtime.color_spaces import ColorRGBA
        from visual_engine.runtime.identity import stable_digest

        if not isinstance(self.canonical_color, ColorRGBA):
            raise BaseColorError("canonical_color must be ColorRGBA")
        if self.authored_representation is not None and not isinstance(self.authored_representation, BaseColorAuthoredRepresentation):
            raise BaseColorError("authored_representation must be BaseColorAuthoredRepresentation or None")
        if not isinstance(self.source, BaseColorSource):
            raise BaseColorError("source must be BaseColorSource")
        if not isinstance(self.provenance, BaseColorProvenance):
            raise BaseColorError("provenance must be BaseColorProvenance")
        if not isinstance(self.role, BaseColorRole):
            raise BaseColorError("role must be BaseColorRole")
        if not isinstance(self.alpha_semantics, AlphaSemantics):
            raise BaseColorError("alpha_semantics must be AlphaSemantics")
        if not isinstance(self.inheritance, BaseColorInheritance):
            raise BaseColorError("inheritance must be BaseColorInheritance")
        if self.source.source_id != self.provenance.source_id:
            raise BaseColorError("BASE source and provenance source_id contradict each other")
        if self.source.component_id != self.provenance.authority_component_id:
            raise BaseColorError("BASE source and provenance authority component contradict each other")
        if not self.provenance.lineage or self.provenance.lineage[0] != self.provenance.authority_component_id:
            raise BaseColorError("BASE provenance lineage must start at the authority component")
        if self.provenance.lineage[-1] != self.provenance.target_component_id:
            raise BaseColorError("BASE provenance lineage must end at the target component")
        if self.source.kind is BaseColorSourceKind.AUTHORED and self.authored_representation is None:
            raise BaseColorError("authored BASE colors must preserve their authored sRGB representation")
        if self.source.kind is BaseColorSourceKind.GENERATED:
            if self.provenance.generator_id is None:
                raise BaseColorError("generated BASE colors require generator provenance")
            if self.authored_representation is not None:
                raise BaseColorError("generated BASE colors cannot claim an authored representation")
        if self.source.kind is BaseColorSourceKind.INHERITED and self.provenance.rule != "inherited-authority":
            raise BaseColorError("inherited BASE colors require inherited-authority provenance")
        expected_alpha = AlphaSemantics.OPAQUE if self.canonical_color.alpha == 1.0 else AlphaSemantics.UNASSOCIATED
        if self.alpha_semantics is not expected_alpha:
            raise BaseColorError(
                f"alpha_semantics={self.alpha_semantics.value!r} contradicts canonical alpha={self.canonical_color.alpha!r}"
            )
        payload = {
            "canonical_color": self.canonical_color,
            "authored_representation": self.authored_representation,
            "source": self.source,
            "provenance": self.provenance,
            "role": self.role,
            "alpha_semantics": self.alpha_semantics,
            "inheritance": self.inheritance,
        }
        object.__setattr__(self, "fingerprint", stable_digest(payload))

    @classmethod
    def from_srgb(
        cls,
        component_id: str,
        value: str,
        *,
        source_id: str | None = None,
        role: BaseColorRole = BaseColorRole.PRIMARY,
        inheritance: BaseColorInheritance | None = None,
    ) -> "BaseColor":
        from visual_engine.runtime.color_spaces import ColorRGBA

        source_id = source_id or f"base:{component_id}"
        color = ColorRGBA.from_hex(value)
        authored = BaseColorAuthoredRepresentation("srgb", value)
        alpha = AlphaSemantics.OPAQUE if color.alpha == 1.0 else AlphaSemantics.UNASSOCIATED
        return cls(
            canonical_color=color,
            authored_representation=authored,
            source=BaseColorSource(BaseColorSourceKind.AUTHORED, source_id, component_id),
            provenance=BaseColorProvenance(
                target_component_id=component_id,
                authority_component_id=component_id,
                source_id=source_id,
                lineage=(component_id,),
            ),
            role=role,
            alpha_semantics=alpha,
            inheritance=inheritance or BaseColorInheritance(),
        )

    @classmethod
    def generated_from_srgb(
        cls,
        component_id: str,
        value: str,
        *,
        generator_id: str,
        generator_version: str,
        source_id: str | None = None,
        role: BaseColorRole = BaseColorRole.PRIMARY,
        inheritance: BaseColorInheritance | None = None,
    ) -> "BaseColor":
        from visual_engine.runtime.color_spaces import ColorRGBA

        source_id = source_id or f"generated:{generator_id}:{component_id}"
        color = ColorRGBA.from_hex(value)
        alpha = AlphaSemantics.OPAQUE if color.alpha == 1.0 else AlphaSemantics.UNASSOCIATED
        return cls(
            canonical_color=color,
            authored_representation=None,
            source=BaseColorSource(BaseColorSourceKind.GENERATED, source_id, component_id),
            provenance=BaseColorProvenance(
                target_component_id=component_id,
                authority_component_id=component_id,
                source_id=source_id,
                lineage=(component_id,),
                rule="generated-authority",
                generator_id=generator_id,
                generator_version=generator_version,
            ),
            role=role,
            alpha_semantics=alpha,
            inheritance=inheritance or BaseColorInheritance(),
        )

    def inherited_for(
        self,
        target_component_id: str,
        *,
        lineage: tuple[str, ...],
    ) -> "BaseColor":
        """Carry one authority into a descendant without changing its color."""
        if not self.inheritance.allow_children:
            raise BaseColorError("BASE authority does not allow inheritance")
        if not target_component_id or not lineage:
            raise BaseColorError("inherited BASE resolution requires target and lineage")
        if self.provenance.authority_component_id in lineage and lineage[-1] != target_component_id:
            raise BaseColorError("inherited BASE lineage is not ordered toward the target")
        return type(self)(
            canonical_color=self.canonical_color,
            authored_representation=self.authored_representation,
            source=BaseColorSource(BaseColorSourceKind.INHERITED, self.source.source_id, self.source.component_id),
            provenance=BaseColorProvenance(
                target_component_id=target_component_id,
                authority_component_id=self.provenance.authority_component_id,
                source_id=self.provenance.source_id,
                lineage=lineage,
                rule="inherited-authority",
                generator_id=self.provenance.generator_id,
                generator_version=self.provenance.generator_version,
            ),
            role=self.role,
            alpha_semantics=self.alpha_semantics,
            inheritance=self.inheritance,
        )
