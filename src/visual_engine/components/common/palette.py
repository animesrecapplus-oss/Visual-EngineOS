from __future__ import annotations

"""Typed, renderer-neutral palette authority.

V1.26 models a palette as one semantic authority containing zero or more named
color slots.  It deliberately does not mix slots, composite alpha, apply
lighting, or infer style.  V1.27 composition consumes this contract without
turning the palette into a hidden renderer operation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # pragma: no cover
    from visual_engine.runtime.color_spaces import ColorRGBA


class PaletteError(ValueError):
    """Raised when a palette violates its closed semantic contract."""


class PaletteSlot(str, Enum):
    PRIMARY = "primary"
    SECONDARY = "secondary"
    ACCENT = "accent"
    DETAIL = "detail"


class PaletteSourceKind(str, Enum):
    AUTHORED = "authored"
    INHERITED = "inherited"
    GENERATED = "generated"


class PaletteOverridePolicy(str, Enum):
    LOCAL_WINS = "local-wins"
    INHERIT_WINS = "inherit-wins"
    REJECT_CONFLICT = "reject-conflict"


@dataclass(frozen=True, slots=True)
class PaletteAuthoredRepresentation:
    """Exact authored sRGB spelling for one palette slot."""

    slot: PaletteSlot
    value: str
    color_space: str = "srgb"

    def __post_init__(self) -> None:
        if not isinstance(self.slot, PaletteSlot):
            raise PaletteError("authored palette slot must be a PaletteSlot")
        if self.color_space != "srgb":
            raise PaletteError("palette authored representation must be sRGB")
        if not isinstance(self.value, str) or len(self.value) not in (7, 9) or not self.value.startswith("#"):
            raise PaletteError("authored palette value must be #RRGGBB or #RRGGBBAA")
        try:
            int(self.value[1:], 16)
        except ValueError as exc:
            raise PaletteError("authored palette value must be hexadecimal") from exc


@dataclass(frozen=True, slots=True)
class PaletteEntry:
    """One semantic palette slot in canonical linear-sRGB RGBA."""

    slot: PaletteSlot
    canonical_color: "ColorRGBA"
    authored_representation: PaletteAuthoredRepresentation | None = None

    def __post_init__(self) -> None:
        from visual_engine.runtime.color_spaces import ColorRGBA

        if not isinstance(self.slot, PaletteSlot):
            raise PaletteError("palette entry slot must be a PaletteSlot")
        if not isinstance(self.canonical_color, ColorRGBA):
            raise PaletteError("palette entry canonical_color must be ColorRGBA")
        if self.authored_representation is not None:
            if self.authored_representation.slot is not self.slot:
                raise PaletteError("palette authored slot contradicts entry slot")
            expected = ColorRGBA.from_hex(self.authored_representation.value)
            if expected != self.canonical_color:
                raise PaletteError("palette authored sRGB value contradicts canonical color")


@dataclass(frozen=True, slots=True)
class PaletteSource:
    kind: PaletteSourceKind
    source_id: str
    component_id: str

    def __post_init__(self) -> None:
        if not isinstance(self.kind, PaletteSourceKind):
            raise PaletteError("palette source kind is invalid")
        if not self.source_id or not self.component_id:
            raise PaletteError("palette source_id and component_id are required")


@dataclass(frozen=True, slots=True)
class PaletteProvenance:
    target_component_id: str
    authority_component_id: str
    source_id: str
    lineage: tuple[str, ...]
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
                raise PaletteError(f"palette provenance {name} must be non-empty")
        if not self.lineage:
            raise PaletteError("palette provenance lineage must not be empty")
        if self.lineage[0] != self.authority_component_id or self.lineage[-1] != self.target_component_id:
            raise PaletteError("palette provenance lineage must run authority -> target")
        if len(set(self.lineage)) != len(self.lineage):
            raise PaletteError("palette provenance lineage must not repeat component IDs")
        if (self.generator_id is None) != (self.generator_version is None):
            raise PaletteError("palette generator_id and generator_version must be provided together")
        if self.generator_id is not None and not self.generator_id:
            raise PaletteError("palette generator_id must be non-empty")
        if self.generator_version is not None and not self.generator_version:
            raise PaletteError("palette generator_version must be non-empty")


@dataclass(frozen=True, slots=True)
class PaletteInheritance:
    allow_children: bool = True
    override_policy: PaletteOverridePolicy = PaletteOverridePolicy.LOCAL_WINS

    def __post_init__(self) -> None:
        if not isinstance(self.allow_children, bool):
            raise PaletteError("PaletteInheritance.allow_children must be boolean")
        if not isinstance(self.override_policy, PaletteOverridePolicy):
            raise PaletteError("unsupported palette override policy")


@dataclass(frozen=True, slots=True)
class Palette:
    """One whole-palette authority for a component.

    Entries are stored as a tuple rather than a dict so duplicate semantic slots
    can be detected and rejected before canonicalization. Missing slots remain
    missing; no implicit fallback or cross-authority slot mixing is allowed.
    """

    entries: tuple[PaletteEntry, ...]
    source: PaletteSource
    provenance: PaletteProvenance
    inheritance: PaletteInheritance = field(default_factory=PaletteInheritance)
    fingerprint: str = field(init=False)

    def __post_init__(self) -> None:
        from visual_engine.runtime.identity import stable_digest

        if not isinstance(self.entries, tuple):
            raise PaletteError("palette entries must be a tuple")
        seen: set[PaletteSlot] = set()
        for entry in self.entries:
            if not isinstance(entry, PaletteEntry):
                raise PaletteError("palette entries must contain PaletteEntry instances")
            if entry.slot in seen:
                raise PaletteError(f"duplicate palette slot: {entry.slot.value}")
            seen.add(entry.slot)
        if not isinstance(self.source, PaletteSource):
            raise PaletteError("palette source is invalid")
        if not isinstance(self.provenance, PaletteProvenance):
            raise PaletteError("palette provenance is invalid")
        if not isinstance(self.inheritance, PaletteInheritance):
            raise PaletteError("palette inheritance is invalid")
        if self.source.source_id != self.provenance.source_id:
            raise PaletteError("palette source and provenance source_id contradict each other")
        if self.source.component_id != self.provenance.authority_component_id:
            raise PaletteError("palette source and provenance authority contradict each other")
        if self.source.kind is PaletteSourceKind.AUTHORED:
            if any(entry.authored_representation is None for entry in self.entries):
                raise PaletteError("authored palettes require authored sRGB representation for every entry")
        if self.source.kind is PaletteSourceKind.GENERATED:
            if self.provenance.generator_id is None:
                raise PaletteError("generated palettes require generator provenance")
            if any(entry.authored_representation is not None for entry in self.entries):
                raise PaletteError("generated palettes cannot claim authored representations")
        if self.source.kind is PaletteSourceKind.INHERITED and self.provenance.rule != "inherited-authority":
            raise PaletteError("inherited palettes require inherited-authority provenance")
        payload = {
            "entries": self.entries,
            "source": self.source,
            "provenance": self.provenance,
            "inheritance": self.inheritance,
        }
        object.__setattr__(self, "fingerprint", stable_digest(payload))

    @property
    def slots(self) -> tuple[PaletteSlot, ...]:
        return tuple(entry.slot for entry in self.entries)

    def get(self, slot: PaletteSlot) -> PaletteEntry | None:
        if not isinstance(slot, PaletteSlot):
            raise PaletteError("palette slot must be a PaletteSlot")
        return next((entry for entry in self.entries if entry.slot is slot), None)

    @classmethod
    def from_srgb(
        cls,
        component_id: str,
        values: dict[PaletteSlot, str],
        *,
        source_id: str | None = None,
        inheritance: PaletteInheritance | None = None,
    ) -> "Palette":
        from visual_engine.runtime.color_spaces import ColorRGBA

        source_id = source_id or f"palette:{component_id}"
        entries = []
        for slot, value in sorted(values.items(), key=lambda item: item[0].value):
            if not isinstance(slot, PaletteSlot):
                raise PaletteError("palette values keys must be PaletteSlot instances")
            color = ColorRGBA.from_hex(value)
            entries.append(PaletteEntry(slot, color, PaletteAuthoredRepresentation(slot, value)))
        return cls(
            tuple(entries),
            PaletteSource(PaletteSourceKind.AUTHORED, source_id, component_id),
            PaletteProvenance(component_id, component_id, source_id, (component_id,)),
            inheritance or PaletteInheritance(),
        )

    @classmethod
    def generated_from_srgb(
        cls,
        component_id: str,
        values: dict[PaletteSlot, str],
        *,
        generator_id: str,
        generator_version: str,
        source_id: str | None = None,
        inheritance: PaletteInheritance | None = None,
    ) -> "Palette":
        from visual_engine.runtime.color_spaces import ColorRGBA

        source_id = source_id or f"generated-palette:{generator_id}:{component_id}"
        entries = tuple(
            PaletteEntry(slot, ColorRGBA.from_hex(value))
            for slot, value in sorted(values.items(), key=lambda item: item[0].value)
        )
        return cls(
            entries,
            PaletteSource(PaletteSourceKind.GENERATED, source_id, component_id),
            PaletteProvenance(component_id, component_id, source_id, (component_id,), "generated-authority", generator_id, generator_version),
            inheritance or PaletteInheritance(),
        )

    def inherited_for(self, target_component_id: str, *, lineage: tuple[str, ...]) -> "Palette":
        if not self.inheritance.allow_children:
            raise PaletteError("palette authority does not allow inheritance")
        if not target_component_id or not lineage:
            raise PaletteError("inherited palette requires target and lineage")
        return type(self)(
            self.entries,
            PaletteSource(PaletteSourceKind.INHERITED, self.source.source_id, self.source.component_id),
            PaletteProvenance(
                target_component_id=target_component_id,
                authority_component_id=self.provenance.authority_component_id,
                source_id=self.provenance.source_id,
                lineage=lineage,
                rule="inherited-authority",
                generator_id=self.provenance.generator_id,
                generator_version=self.provenance.generator_version,
            ),
            self.inheritance,
        )
