from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import math

from .visual_contract import LocalTransform, VisualContract, VisualOverrides
from .geometry_contract import GeometryContract
from .base_color import BaseColor
from .palette import Palette

class ConstraintKind(str, Enum):
    HARD = "hard"
    SOFT = "soft"
    STATISTICAL = "statistical"
    AESTHETIC = "aesthetic"

@dataclass(frozen=True, slots=True)
class Parameter:
    name: str
    value: Any
    min_value: float | None = None
    max_value: float | None = None
    def __post_init__(self) -> None:
        if not self.name: raise ValueError("Parameter name must not be empty")
        if isinstance(self.value, (int, float)) and not isinstance(self.value, bool):
            if not math.isfinite(float(self.value)): raise ValueError("Parameter numeric value must be finite")
            if self.min_value is not None and float(self.value) < self.min_value: raise ValueError("Parameter below minimum")
            if self.max_value is not None and float(self.value) > self.max_value: raise ValueError("Parameter above maximum")

@dataclass(frozen=True, slots=True)
class Anchor:
    name: str
    x: float = 0.0
    y: float = 0.0
    z: float = 0.0
    def __post_init__(self) -> None:
        if not self.name or not all(math.isfinite(v) for v in (self.x,self.y,self.z)):
            raise ValueError("Anchor must have a name and finite coordinates")

@dataclass(frozen=True, slots=True)
class Relation:
    source_id: str
    relation_type: str
    target_id: str
    metadata: dict[str, Any] = field(default_factory=dict)
    def __post_init__(self) -> None:
        if not self.source_id or not self.relation_type or not self.target_id:
            raise ValueError("Relation endpoints and type are required")

@dataclass(frozen=True, slots=True)
class Constraint:
    name: str
    kind: ConstraintKind
    expression: str
    weight: float = 1.0
    def __post_init__(self) -> None:
        if not self.name or not self.expression: raise ValueError("Constraint requires name and expression")
        if not math.isfinite(self.weight) or self.weight < 0: raise ValueError("Constraint weight must be finite and >= 0")

@dataclass(frozen=True, slots=True)
class Profile:
    name: str
    values: dict[str, Any] = field(default_factory=dict)

@dataclass(frozen=True, slots=True)
class AppearanceLayer:
    name: str
    values: dict[str, Any] = field(default_factory=dict)
    opacity: float = 1.0
    def __post_init__(self) -> None:
        if not 0 <= self.opacity <= 1 or not math.isfinite(self.opacity): raise ValueError("Appearance opacity must be in [0,1]")

@dataclass(frozen=True, slots=True)
class StateLayer:
    name: str
    values: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True
    priority: int = 0
    group: str | None = None
    conflicts: tuple[str, ...] = ()
    requires: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.name:
            raise ValueError("State name must not be empty")
        if not isinstance(self.priority, int):
            raise ValueError("State priority must be an integer")
        if self.group is not None and not self.group:
            raise ValueError("State group must be non-empty when provided")
        for field_name, values in (("conflicts", self.conflicts), ("requires", self.requires)):
            if any(not isinstance(v, str) or not v for v in values):
                raise ValueError(f"State {field_name} entries must be non-empty strings")
            if len(set(values)) != len(values):
                raise ValueError(f"State {field_name} entries must be unique")
            if self.name in values:
                raise ValueError(f"State {field_name} cannot contain the state itself")

@dataclass(slots=True)
class Component:
    id: str
    kind: str
    parameters: dict[str, Parameter] = field(default_factory=dict)
    anchors: dict[str, Anchor] = field(default_factory=dict)
    relations: list[Relation] = field(default_factory=list)
    constraints: list[Constraint] = field(default_factory=list)
    profiles: dict[str, Profile] = field(default_factory=dict)
    appearance: list[AppearanceLayer] = field(default_factory=list)
    # V1.25: one typed local BASE authority; inheritance is resolved separately.
    base_color: BaseColor | None = None
    # V1.26: one typed local palette authority; slot selection is resolved later.
    palette: Palette | None = None
    state: list[StateLayer] = field(default_factory=list)
    children: list["Component"] = field(default_factory=list)
    parent_id: str | None = None
    transform: LocalTransform = field(default_factory=LocalTransform)
    visual: VisualContract = field(default_factory=VisualContract)
    visual_overrides: VisualOverrides | None = None
    geometry: GeometryContract = field(default_factory=GeometryContract)
    def __post_init__(self) -> None:
        if not self.id or not self.kind: raise ValueError("Component id and kind are required")
        if self.base_color is not None and not isinstance(self.base_color, BaseColor):
            raise ValueError("Component.base_color must be a BaseColor")
        if self.palette is not None and not isinstance(self.palette, Palette):
            raise ValueError("Component.palette must be a Palette")
    def add_child(self, child: "Component") -> None:
        if child.id == self.id: raise ValueError("Component cannot be its own child")
        # Construction must remain O(1) per insertion. Global uniqueness is a
        # RuntimeGraph invariant; scanning the whole subtree here made bulk entity
        # construction accidentally O(n²). Sibling duplicates are still rejected
        # immediately because they are unambiguous at this boundary.
        if any(existing.id == child.id for existing in self.children):
            raise ValueError(f"Duplicate component id: {child.id}")
        child.parent_id = self.id
        self.children.append(child)
    def set_parameter(self, parameter: Parameter) -> None: self.parameters[parameter.name] = parameter
    def add_constraint(self, constraint: Constraint) -> None: self.constraints.append(constraint)
    def add_appearance(self, layer: AppearanceLayer) -> None: self.appearance.append(layer)
    def add_state(self, layer: StateLayer) -> None: self.state.append(layer)
    def walk(self):
        yield self
        for child in self.children: yield from child.walk()
    def find(self, component_id: str) -> "Component | None":
        for component in self.walk():
            if component.id == component_id: return component
        return None
