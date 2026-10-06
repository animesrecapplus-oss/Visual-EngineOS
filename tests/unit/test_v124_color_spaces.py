import math
import pytest

from visual_engine.runtime.color_spaces import (
    ColorRGBA,
    ColorSpace,
    ColorSpaceError,
    canonicalize_hex_color,
    linear_channel_to_srgb,
    srgb_channel_to_linear,
)


def test_srgb_transfer_uses_linear_light_not_gamma_as_a_linear_identity():
    assert srgb_channel_to_linear(0.0) == 0.0
    assert srgb_channel_to_linear(1.0) == 1.0
    assert srgb_channel_to_linear(0.5) == pytest.approx(0.21404114048223255, abs=1e-15)
    assert linear_channel_to_srgb(0.21404114048223255) == pytest.approx(0.5, abs=1e-15)


def test_canonical_storage_is_linear_srgb_and_alpha_is_unassociated():
    color = ColorRGBA.from_hex("#80808080")
    assert color.red == pytest.approx(0.21586050011389926)
    assert color.green == color.red
    assert color.blue == color.red
    assert color.alpha == pytest.approx(128 / 255)
    assert color.to_rgba8() == (128, 128, 128, 128)


def test_hex_roundtrip_is_exact_for_a_representative_8bit_grid():
    for red in range(0, 256, 17):
        for green in range(0, 256, 17):
            for blue in range(0, 256, 17):
                source = f"#{red:02x}{green:02x}{blue:02x}"
                assert ColorRGBA.from_hex(source).to_hex() == source


def test_alpha_roundtrip_is_exact_for_all_8bit_alpha_values_at_fixed_rgb():
    for alpha in range(256):
        source = f"#123456{alpha:02x}"
        assert ColorRGBA.from_hex(source).to_hex(include_alpha=True) == source


def test_known_xyz_d65_reference_values():
    red = ColorRGBA.from_hex("#ff0000").to_space(ColorSpace.XYZ_D65)
    white = ColorRGBA.from_hex("#ffffff").to_space(ColorSpace.XYZ_D65)
    assert red == pytest.approx((0.4124564, 0.2126729, 0.0193339), abs=2e-7)
    assert white == pytest.approx((0.95047, 1.0000001, 1.08883), abs=2e-7)


def test_known_oklab_reference_for_srgb_red():
    lab = ColorRGBA.from_hex("#ff0000").to_space(ColorSpace.OKLAB)
    assert lab == pytest.approx((0.62795536, 0.22486306, 0.12584630), abs=2e-7)


def test_hsl_roundtrip_preserves_display_color():
    for source in ("#000000", "#ffffff", "#ff0000", "#00ff00", "#0000ff", "#123456", "#abcdef"):
        color = ColorRGBA.from_hex(source)
        hsl = color.to_space(ColorSpace.HSL)
        rebuilt = ColorRGBA.from_space(ColorSpace.HSL, hsl)
        assert rebuilt.to_rgba8()[:3] == color.to_rgba8()[:3]


def test_oklab_roundtrip_has_small_numeric_error_without_gamut_mapping():
    for source in ("#000000", "#ffffff", "#ff0000", "#00ff00", "#0000ff", "#123456", "#abcdef"):
        color = ColorRGBA.from_hex(source)
        rebuilt = ColorRGBA.from_space(ColorSpace.OKLAB, color.to_space(ColorSpace.OKLAB), alpha=color.alpha)
        assert rebuilt.distance_oklab(color) < 1e-7
        assert rebuilt.to_rgba8() == color.to_rgba8()


def test_xyz_roundtrip_has_small_numeric_error():
    for source in ("#000000", "#ffffff", "#ff0000", "#00ff00", "#0000ff", "#808080", "#123456"):
        color = ColorRGBA.from_hex(source)
        rebuilt = ColorRGBA.from_space(ColorSpace.XYZ_D65, color.to_space(ColorSpace.XYZ_D65), alpha=color.alpha)
        assert rebuilt.distance_oklab(color) < 2e-6
        assert rebuilt.to_rgba8() == color.to_rgba8()


def test_out_of_gamut_conversion_rejects_instead_of_clipping():
    with pytest.raises(ColorSpaceError, match="outside the sRGB gamut"):
        ColorRGBA.from_space(ColorSpace.OKLAB, (0.7, 0.5, 0.5))
    with pytest.raises(ColorSpaceError, match="outside the sRGB gamut"):
        ColorRGBA.from_space(ColorSpace.XYZ_D65, (2.0, 0.0, 0.0))


def test_channel_bounds_are_fail_closed():
    with pytest.raises(ColorSpaceError):
        srgb_channel_to_linear(-0.01)
    with pytest.raises(ColorSpaceError):
        linear_channel_to_srgb(1.01)
    with pytest.raises(ColorSpaceError):
        linear_channel_to_srgb(1.0 + 1e-9)
    with pytest.raises(ColorSpaceError):
        ColorRGBA.from_hex("#12zz34")
    with pytest.raises(ColorSpaceError):
        ColorRGBA.from_space(ColorSpace.HSL, (1.1, 0.5, 0.5))


def test_gray_hsl_hue_is_canonicalized_to_zero_because_hue_is_undefined():
    hue, saturation, lightness = ColorRGBA.from_hex("#808080").to_space(ColorSpace.HSL)
    assert hue == 0.0
    assert saturation == 0.0
    assert lightness == pytest.approx(128 / 255)


def test_canonicalize_hex_preserves_engine_encoded_channels():
    assert canonicalize_hex_color("#AABBCC") == "#aabbcc"
    assert canonicalize_hex_color("#AABBCC80", preserve_alpha_channel=True) == "#aabbcc80"
    assert canonicalize_hex_color("#AABBCC", preserve_alpha_channel=True) == "#aabbccff"


def test_alpha_does_not_change_rgb_conversion():
    opaque = ColorRGBA.from_hex("#336699")
    translucent = ColorRGBA.from_hex("#33669940")
    assert opaque.to_space(ColorSpace.OKLAB) == pytest.approx(translucent.to_space(ColorSpace.OKLAB), abs=1e-12)
    assert translucent.alpha == pytest.approx(64 / 255)


def test_no_nan_or_infinite_values_can_enter_the_canonical_color():
    for value in (math.nan, math.inf, -math.inf):
        with pytest.raises(ColorSpaceError):
            ColorRGBA(value, 0.0, 0.0)
