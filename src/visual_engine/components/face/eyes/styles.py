from __future__ import annotations

from dataclasses import replace

from .appearance.spec import EyeAppearance
from .iris.spec import IrisSpec
from .lashes.spec import LashSpec, LowerLashSpec
from .eyebrow.spec import BrowSpec
from .pupil.spec import PupilSpec
from .highlights.spec import ReflectionMark


def anime_golden() -> EyeAppearance:
    """Preset based only on visible characteristics of the supplied close-up reference."""
    return EyeAppearance(
        sclera="#ffffff",
        conjunctiva_color="#ffffff",
        outline="#000000",
        iris=IrisSpec(
            shape="circle",
            color="#f4d20a",
            inner_color="#f09a06",
            outer_color="#ffec4a",
            pattern="radial",
            ring_count=2,
            glow=0.18,
            opacity=1.0,
            pattern_strength=0.38,
            pattern_count=16,
        ),
        pupils=(PupilSpec(scale=0.7, color="#9a4b00"),),
        lashes=LashSpec(enabled=True, density=0.98, length=0.075, thickness=0.022, curvature=0.65, color="#000000", count=20, style="anime", outer_flare=0.28, upward_bias=0.18, form="tapered"),
        lower_lashes=LowerLashSpec(enabled=True, density=0.10, length=0.022, thickness=0.004, color="#777777", opacity=0.28, count=6, style="anime", outer_flare=0.18),
        eyebrow=BrowSpec(enabled=True, shape="arched", length=0.85, thickness=0.08, density=0.85, color="#000000"),
        reflection="#ffffff",
        reflection_opacity=0.9,
        reflection_marks=(
            ReflectionMark("circle", -0.25, -0.25, 0.12, 0.12, "#ffffff", 0.95),
            ReflectionMark("circle", -0.12, -0.18, 0.05, 0.05, "#ffffff", 0.9),
            ReflectionMark("ellipse", 0.25, 0.30, 0.10, 0.06, "#fffef0", 0.9, -12.0),
        ),
    )


def reflective_scene_eye() -> EyeAppearance:
    """Preset exposing the structured-reflection capability seen in the second reference."""
    return EyeAppearance(
        sclera="#f5f5e9",
        conjunctiva_color="#ffffff",
        outline="#000000",
        iris=IrisSpec(
            shape="circle",
            color="#a5a22e",
            inner_color="#e1dc57",
            outer_color="#6e701c",
            pattern="radial",
            ring_count=4,
            glow=0.08,
            opacity=0.98,
            pattern_strength=0.25,
            pattern_count=18,
        ),
        pupils=(PupilSpec(scale=0.48, color="#151509"),),
        lashes=LashSpec(enabled=True, density=0.92, length=0.10, thickness=0.024, curvature=0.30, color="#000000", count=16, style="natural", outer_flare=0.20, upward_bias=0.20),
        lower_lashes=LowerLashSpec(enabled=True, density=0.18, length=0.038, thickness=0.006, color="#777777", opacity=0.24, count=5, style="natural", outer_flare=0.16),
        eyebrow=BrowSpec(enabled=False),
        reflection="#ffffff",
        reflection_opacity=0.75,
        reflection_marks=(
            ReflectionMark("ellipse", 0.05, -0.18, 0.30, 0.08, "#ffffff", 0.75, -15.0),
            ReflectionMark("ellipse", -0.20, -0.25, 0.14, 0.05, "#eaffd5", 0.48, 18.0),
            ReflectionMark("diamond", 0.20, 0.18, 0.07, 0.07, "#f8ffcf", 0.42, 10.0),
        ),
    )
