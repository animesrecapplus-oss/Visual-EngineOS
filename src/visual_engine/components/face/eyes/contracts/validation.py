import math
import re

_HEX = re.compile(r"^#(?:[0-9a-fA-F]{3}|[0-9a-fA-F]{4}|[0-9a-fA-F]{6}|[0-9a-fA-F]{8})$")

def _finite(values: tuple[float, ...]) -> bool:
    return all(math.isfinite(float(v)) for v in values)

def _color(value: str, name: str) -> None:
    if not isinstance(value, str) or not _HEX.fullmatch(value):
        raise ValueError(f"{name} must be a CSS hex color (#RGB, #RGBA, #RRGGBB or #RRGGBBAA)")
