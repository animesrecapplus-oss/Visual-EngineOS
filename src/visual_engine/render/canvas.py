from __future__ import annotations
from dataclasses import dataclass, field
import math
import numpy as np
from visual_engine.geometry import Circle

@dataclass(slots=True)
class Canvas:
    width: int
    height: int
    rgba: np.ndarray = field(init=False, repr=False)
    def __post_init__(self) -> None:
        if self.width <= 0 or self.height <= 0: raise ValueError("Canvas dimensions must be positive")
        self.rgba = np.zeros((self.height,self.width,4), dtype=np.float32)
    def clear(self, color) -> None:
        self._validate_color(color); self.rgba[...] = color
    def fill_circle(self, circle: Circle, color) -> None:
        self._validate_color(color)
        x0,y0,x1,y1=circle.bounds(); ix0=max(0,math.floor(x0)); iy0=max(0,math.floor(y0)); ix1=min(self.width-1,math.ceil(x1)); iy1=min(self.height-1,math.ceil(y1))
        if ix0>ix1 or iy0>iy1:return
        yy,xx=np.mgrid[iy0:iy1+1,ix0:ix1+1]; inside=(xx-circle.center.x)**2+(yy-circle.center.y)**2<=circle.radius**2
        region=self.rgba[iy0:iy1+1,ix0:ix1+1]; src=np.asarray(color,dtype=np.float32); a=src[3]
        region[inside,:3]=src[:3]*a+region[inside,:3]*(1-a); region[inside,3]=a+region[inside,3]*(1-a)
    def to_uint8(self) -> np.ndarray: return np.clip(np.rint(self.rgba*255),0,255).astype(np.uint8)
    @staticmethod
    def _validate_color(color) -> None:
        if len(color)!=4 or not all(math.isfinite(float(v)) for v in color): raise ValueError("RGBA color must contain four finite values")
        if not all(0<=float(v)<=1 for v in color): raise ValueError("RGBA values must be within [0, 1]")
