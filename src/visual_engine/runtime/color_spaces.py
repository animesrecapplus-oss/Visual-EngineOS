from __future__ import annotations

"""Canonical color-space primitives for the appearance runtime.

The engine keeps one canonical internal representation: **linear sRGB RGBA**.
External sRGB hexadecimal values are display-encoded and are decoded before any
future arithmetic.  HSL and OKLab are exposed as explicit conversion spaces;
XYZ D65 is retained as the connection space for standards-oriented workflows.

This module intentionally does *not* perform gamut mapping, tone mapping,
alpha compositing, lighting, shading or palette generation.  Out-of-gamut
conversions fail closed instead of silently clipping a color into a different
visual result.
"""

from dataclasses import dataclass
from enum import Enum
import math
from typing import Iterable


class ColorSpace(str, Enum):
    """Supported color coordinate systems and their explicit semantics."""

    SRGB = "srgb"
    LINEAR_SRGB = "linear-srgb"
    XYZ_D65 = "xyz-d65"
    HSL = "hsl"
    OKLAB = "oklab"


class ColorSpaceError(ValueError):
    """Raised when color coordinates are malformed or outside their contract."""


_EPSILON = 1e-12
_MATRIX_GAMUT_EPSILON = 2e-7

# IEC-style sRGB / CIE D65 matrices.  Constants are kept explicit so the
# conversion path is auditable and deterministic rather than delegated to a
# renderer-specific color library.
_LINEAR_SRGB_TO_XYZ_D65 = (
    (0.4124564, 0.3575761, 0.1804375),
    (0.2126729, 0.7151522, 0.0721750),
    (0.0193339, 0.1191920, 0.9503041),
)
_XYZ_D65_TO_LINEAR_SRGB = (
    (3.2404542, -1.5371385, -0.4985314),
    (-0.9692660, 1.8760108, 0.0415560),
    (0.0556434, -0.2040259, 1.0572252),
)

# OKLab matrices from the published OKLab construction, using linear sRGB as
# the source space.  The cube-root stage is signed so the inverse remains
# mathematically defined for intermediate negative XYZ/LMS values; gamut is
# checked only at the canonical linear-sRGB boundary.
_LINEAR_SRGB_TO_LMS = (
    (0.4122214708, 0.5363325363, 0.0514459929),
    (0.2119034982, 0.6806995451, 0.1073969566),
    (0.0883024619, 0.2817188376, 0.6299787005),
)
_LMS_TO_OKLAB = (
    (0.2104542553, 0.7936177850, -0.0040720468),
    (1.9779984951, -2.4285922050, 0.4505937099),
    (0.0259040371, 0.7827717662, -0.8086757660),
)
_OKLAB_TO_LMS = (
    (1.0, 0.3963377774, 0.2158037573),
    (1.0, -0.1055613458, -0.0638541728),
    (1.0, -0.0894841775, -1.2914855480),
)
_LMS_TO_LINEAR_SRGB = (
    (4.0767416621, -3.3077115913, 0.2309699292),
    (-1.2684380046, 2.6097574011, -0.3413193965),
    (-0.0041960863, -0.7034186147, 1.7076147010),
)


def _finite(value: float, name: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise ColorSpaceError(f"{name} must be finite")
    return result


def _unit(value: float, name: str) -> float:
    result = _finite(value, name)
    if not 0.0 <= result <= 1.0:
        raise ColorSpaceError(f"{name} must be in [0,1]")
    return result


def _triplet(values: Iterable[float], name: str) -> tuple[float, float, float]:
    values = tuple(values)
    if len(values) != 3:
        raise ColorSpaceError(f"{name} requires exactly three channels")
    return tuple(_finite(value, f"{name}[{index}]") for index, value in enumerate(values))  # type: ignore[return-value]


def _matrix3(matrix, values: tuple[float, float, float]) -> tuple[float, float, float]:
    return tuple(
        sum(matrix[row][column] * values[column] for column in range(3))
        for row in range(3)
    )  # type: ignore[return-value]


def _clamp_near_unit(value: float, name: str) -> float:
    """Remove only matrix-inversion noise at a physical [0,1] boundary."""
    if -_MATRIX_GAMUT_EPSILON <= value <= _MATRIX_GAMUT_EPSILON:
        return 0.0
    if 1.0 - _MATRIX_GAMUT_EPSILON <= value <= 1.0 + _MATRIX_GAMUT_EPSILON:
        return 1.0
    if value < 0.0 or value > 1.0:
        raise ColorSpaceError(f"{name} is outside the sRGB gamut: {value!r}")
    return value


def _strict_unit(value: float, name: str) -> float:
    value = _finite(value, name)
    if not 0.0 <= value <= 1.0:
        raise ColorSpaceError(f"{name} must be in [0,1]")
    return value


def srgb_channel_to_linear(value: float) -> float:
    """Decode one IEC sRGB encoded channel into linear-light sRGB."""
    value = _strict_unit(value, "sRGB channel")
    if value <= 0.04045:
        return value / 12.92
    return ((value + 0.055) / 1.055) ** 2.4


def linear_channel_to_srgb(value: float) -> float:
    """Encode one linear-light sRGB channel without clipping."""
    value = _strict_unit(value, "linear sRGB channel")
    if value <= 0.0031308:
        return 12.92 * value
    return 1.055 * (value ** (1.0 / 2.4)) - 0.055


def _hue_to_rgb(p: float, q: float, t: float) -> float:
    t %= 1.0
    if t < 1.0 / 6.0:
        return p + (q - p) * 6.0 * t
    if t < 1.0 / 2.0:
        return q
    if t < 2.0 / 3.0:
        return p + (q - p) * (2.0 / 3.0 - t) * 6.0
    return p


def _hsl_to_srgb(h: float, s: float, l: float) -> tuple[float, float, float]:
    h = _unit(h, "HSL hue")
    s = _unit(s, "HSL saturation")
    l = _unit(l, "HSL lightness")
    if s == 0.0:
        return (l, l, l)
    q = l * (1.0 + s) if l < 0.5 else l + s - l * s
    p = 2.0 * l - q
    return (
        _hue_to_rgb(p, q, h + 1.0 / 3.0),
        _hue_to_rgb(p, q, h),
        _hue_to_rgb(p, q, h - 1.0 / 3.0),
    )


def _srgb_to_hsl(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    r, g, b = rgb
    maximum = max(rgb)
    minimum = min(rgb)
    lightness = (maximum + minimum) / 2.0
    if maximum == minimum:
        return (0.0, 0.0, lightness)
    delta = maximum - minimum
    saturation = delta / (2.0 - maximum - minimum) if lightness > 0.5 else delta / (maximum + minimum)
    if maximum == r:
        hue = ((g - b) / delta + (6.0 if g < b else 0.0)) / 6.0
    elif maximum == g:
        hue = ((b - r) / delta + 2.0) / 6.0
    else:
        hue = ((r - g) / delta + 4.0) / 6.0
    return (hue % 1.0, saturation, lightness)


def _cbrt_signed(value: float) -> float:
    return math.copysign(abs(value) ** (1.0 / 3.0), value)


def _linear_srgb_to_oklab(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    lms = _matrix3(_LINEAR_SRGB_TO_LMS, rgb)
    lms_root = tuple(_cbrt_signed(value) for value in lms)
    return _matrix3(_LMS_TO_OKLAB, lms_root)


def _oklab_to_linear_srgb(lab: tuple[float, float, float]) -> tuple[float, float, float]:
    lms_root = _matrix3(_OKLAB_TO_LMS, lab)
    lms = tuple(value ** 3 for value in lms_root)
    return _matrix3(_LMS_TO_LINEAR_SRGB, lms)


def _linear_srgb_to_xyz(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    return _matrix3(_LINEAR_SRGB_TO_XYZ_D65, rgb)


def _xyz_to_linear_srgb(xyz: tuple[float, float, float]) -> tuple[float, float, float]:
    return _matrix3(_XYZ_D65_TO_LINEAR_SRGB, xyz)


def _hex_to_srgb(value: str) -> tuple[tuple[float, float, float], float]:
    if not isinstance(value, str) or len(value) not in (7, 9) or not value.startswith("#"):
        raise ColorSpaceError("hex color must be #RRGGBB or #RRGGBBAA")
    try:
        channels = tuple(int(value[index:index + 2], 16) / 255.0 for index in range(1, len(value), 2))
    except ValueError as exc:
        raise ColorSpaceError("hex color contains non-hexadecimal data") from exc
    if len(channels) == 3:
        return channels, 1.0
    return channels[:3], channels[3]


def _srgb_to_hex(rgb: tuple[float, float, float], alpha: float, include_alpha: bool) -> str:
    encoded = tuple(linear_channel_to_srgb(channel) for channel in rgb)
    rgb8 = tuple(int(math.floor(channel * 255.0 + 0.5)) for channel in encoded)
    body = "#" + "".join(f"{channel:02x}" for channel in rgb8)
    if include_alpha:
        alpha8 = int(math.floor(_unit(alpha, "alpha") * 255.0 + 0.5))
        body += f"{alpha8:02x}"
    return body


@dataclass(frozen=True, slots=True)
class ColorRGBA:
    """Canonical immutable color stored as linear-sRGB RGB plus alpha.

    Alpha is intentionally stored separately from RGB transfer functions.  It is
    not premultiplied and is never blended by this module.
    """

    red: float
    green: float
    blue: float
    alpha: float = 1.0

    def __post_init__(self) -> None:
        for name, value in (("red", self.red), ("green", self.green), ("blue", self.blue)):
            _unit(value, f"canonical linear-sRGB {name}")
        _unit(self.alpha, "alpha")

    @classmethod
    def from_hex(cls, value: str) -> "ColorRGBA":
        """Decode an engine sRGB hex color into canonical linear-sRGB RGBA."""
        rgb, alpha = _hex_to_srgb(value)
        linear = tuple(srgb_channel_to_linear(channel) for channel in rgb)
        return cls(*linear, alpha)

    @classmethod
    def from_space(
        cls,
        space: ColorSpace,
        values: Iterable[float],
        *,
        alpha: float = 1.0,
    ) -> "ColorRGBA":
        """Construct canonical color from one explicitly declared coordinate space."""
        if not isinstance(space, ColorSpace):
            raise ColorSpaceError("space must be a ColorSpace")
        alpha = _unit(alpha, "alpha")
        coordinates = _triplet(values, space.value)
        if space is ColorSpace.LINEAR_SRGB:
            rgb = tuple(_clamp_near_unit(value, f"linear-sRGB channel {index}") for index, value in enumerate(coordinates))
        elif space is ColorSpace.SRGB:
            rgb = tuple(srgb_channel_to_linear(value) for value in coordinates)
        elif space is ColorSpace.HSL:
            srgb = _hsl_to_srgb(*coordinates)
            rgb = tuple(srgb_channel_to_linear(value) for value in srgb)
        elif space is ColorSpace.XYZ_D65:
            rgb = _xyz_to_linear_srgb(coordinates)
            rgb = tuple(_clamp_near_unit(value, f"XYZ→sRGB channel {index}") for index, value in enumerate(rgb))
        elif space is ColorSpace.OKLAB:
            rgb = _oklab_to_linear_srgb(coordinates)
            rgb = tuple(_clamp_near_unit(value, f"OKLab→sRGB channel {index}") for index, value in enumerate(rgb))
        else:  # pragma: no cover - defensive against future enum extension
            raise ColorSpaceError(f"unsupported color space: {space}")
        return cls(*rgb, alpha)

    @classmethod
    def from_rgba8(cls, values: Iterable[int]) -> "ColorRGBA":
        """Decode 8-bit RGBA channels without passing through a renderer."""
        values = tuple(values)
        if len(values) != 4 or any(isinstance(v, bool) or not isinstance(v, int) or not 0 <= v <= 255 for v in values):
            raise ColorSpaceError("RGBA8 requires four integer channels in [0,255]")
        return cls.from_hex("#" + "".join(f"{value:02x}" for value in values))

    def to_space(self, space: ColorSpace) -> tuple[float, float, float]:
        """Return RGB/HSL/XYZ/OKLab coordinates without mutating the color."""
        if not isinstance(space, ColorSpace):
            raise ColorSpaceError("space must be a ColorSpace")
        rgb = (self.red, self.green, self.blue)
        if space is ColorSpace.LINEAR_SRGB:
            return rgb
        if space is ColorSpace.SRGB:
            return tuple(linear_channel_to_srgb(value) for value in rgb)
        if space is ColorSpace.HSL:
            return _srgb_to_hsl(tuple(linear_channel_to_srgb(value) for value in rgb))
        if space is ColorSpace.XYZ_D65:
            return _linear_srgb_to_xyz(rgb)
        if space is ColorSpace.OKLAB:
            return _linear_srgb_to_oklab(rgb)
        raise ColorSpaceError(f"unsupported color space: {space}")

    def to_hex(self, *, include_alpha: bool | None = None) -> str:
        """Encode canonical linear-sRGB back to the engine's hexadecimal form."""
        if include_alpha is None:
            include_alpha = self.alpha < 1.0 - _EPSILON
        return _srgb_to_hex((self.red, self.green, self.blue), self.alpha, include_alpha)

    def to_rgba8(self) -> tuple[int, int, int, int]:
        """Return display-encoded 8-bit RGBA with deterministic half-up rounding."""
        encoded = self.to_space(ColorSpace.SRGB)
        return tuple(int(math.floor(channel * 255.0 + 0.5)) for channel in encoded) + (
            int(math.floor(self.alpha * 255.0 + 0.5)),
        )

    def distance_oklab(self, other: "ColorRGBA") -> float:
        """Return Euclidean distance in OKLab; useful for regression diagnostics."""
        if not isinstance(other, ColorRGBA):
            raise TypeError("other must be ColorRGBA")
        a = self.to_space(ColorSpace.OKLAB)
        b = other.to_space(ColorSpace.OKLAB)
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def parse_hex_color(value: str) -> ColorRGBA:
    """Small public convenience wrapper for canonical parsing."""
    return ColorRGBA.from_hex(value)


def canonicalize_hex_color(value: str, *, preserve_alpha_channel: bool | None = None) -> str:
    """Canonicalize an engine hex color through linear-sRGB and back.

    For valid 8-bit sRGB colors this is an identity in encoded channel values;
    it exists to make the transfer-function boundary explicit and testable.
    """
    color = ColorRGBA.from_hex(value)
    return color.to_hex(include_alpha=preserve_alpha_channel)
