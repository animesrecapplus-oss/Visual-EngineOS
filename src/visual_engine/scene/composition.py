from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum
import math
from visual_engine.math import Vec2

class LayoutStrategy(str, Enum):
    CENTER = "center"; GRID = "grid"; ROW = "row"; COLUMN = "column"; PACK = "pack"; FREEFORM = "freeform"; RADIAL = "radial"; STACK = "stack"; AUTO = "auto"
class OverflowPolicy(str, Enum):
    CLIP = "clip"; ALLOW = "allow"; SCALE_TO_FIT = "scale_to_fit"

@dataclass(frozen=True, slots=True)
class Frame:
    width: int
    height: int
    aspect_ratio: float = field(init=False)
    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0: raise ValueError("Frame dimensions must be positive")
        object.__setattr__(self, "aspect_ratio", self.width / self.height)

@dataclass(frozen=True, slots=True)
class Camera:
    x: float = 0.0; y: float = 0.0; z: float = 0.0
    zoom: float = 1.0
    rotation_deg: float = 0.0
    def __post_init__(self) -> None:
        if not all(math.isfinite(v) for v in (self.x,self.y,self.z,self.zoom,self.rotation_deg)) or self.zoom <= 0:
            raise ValueError("Invalid camera")

@dataclass(frozen=True, slots=True)
class Placement:
    entity_id: str
    position: Vec2
    scale: float = 1.0
    z: float = 0.0
    rotation: float = 0.0
    def __post_init__(self) -> None:
        if not self.entity_id or self.scale <= 0 or not all(math.isfinite(v) for v in (self.scale,self.z,self.rotation)): raise ValueError("Invalid placement")

@dataclass(frozen=True, slots=True)
class CompositionPolicy:
    strategy: LayoutStrategy = LayoutStrategy.AUTO
    spacing: float = 1.0
    margin: float = 0.05
    overflow: OverflowPolicy = OverflowPolicy.SCALE_TO_FIT
    allow_overlap: bool = False
    def __post_init__(self) -> None:
        if self.spacing < 0 or not 0 <= self.margin < 0.5: raise ValueError("Invalid composition policy")

def compose(entity_ids: list[str], frame: Frame, policy: CompositionPolicy) -> tuple[Placement, ...]:
    if not entity_ids: return ()
    n = len(entity_ids)
    strategy = policy.strategy
    if strategy is LayoutStrategy.AUTO: strategy = LayoutStrategy.CENTER if n == 1 else LayoutStrategy.GRID
    mx, my = frame.width*policy.margin, frame.height*policy.margin
    usable_w, usable_h = frame.width-2*mx, frame.height-2*my
    if strategy is LayoutStrategy.CENTER:
        return (Placement(entity_ids[0], Vec2(frame.width/2, frame.height/2)),)
    if strategy is LayoutStrategy.ROW:
        step = usable_w / max(n,1)
        return tuple(Placement(e, Vec2(mx + step*(i+0.5), frame.height/2)) for i,e in enumerate(entity_ids))
    if strategy is LayoutStrategy.COLUMN:
        step = usable_h / max(n,1)
        return tuple(Placement(e, Vec2(frame.width/2, my + step*(i+0.5))) for i,e in enumerate(entity_ids))
    cols = max(1, math.ceil(math.sqrt(n * frame.width / frame.height)))
    rows = math.ceil(n/cols)
    cw, ch = usable_w/cols, usable_h/rows
    return tuple(Placement(e, Vec2(mx+cw*(i%cols+0.5), my+ch*(i//cols+0.5))) for i,e in enumerate(entity_ids))
