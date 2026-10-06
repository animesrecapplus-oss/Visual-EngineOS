from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

GazeIntentName = Literal[
    "look_forward", "look_left", "look_right", "look_up", "look_down",
    "look_behind_right_eye", "look_behind_left_eye", "look_behind_both_eyes",
    "rotate_globe_alignment_positive", "rotate_globe_alignment_negative",
]


@dataclass(frozen=True, slots=True)
class OcularPromptIntent:
    """Prompt-facing ocular intent vocabulary.

    Names are stable semantic handles, not renderer commands. ``look_behind_*``
    deliberately records a depth yaw that the current 2D GazeSolver cannot render
    as a physically complete eyeball rotation. This prevents a future prompt parser
    from silently translating "behind" into an arbitrary screen-left/right gaze.
    """
    name: GazeIntentName
    eye: Literal["left", "right", "both"] = "both"
    yaw_deg: float = 0.0
    pitch_deg: float = 0.0
    requires_depth_projection: bool = False
    alignment_axis_rotation_deg: float = 0.0

    @property
    def is_depth_intent(self) -> bool:
        return self.requires_depth_projection or abs(self.yaw_deg) > 90.0 or abs(self.pitch_deg) > 90.0


_INTENTS: dict[str, OcularPromptIntent] = {
    "look_forward": OcularPromptIntent("look_forward"),
    "look_left": OcularPromptIntent("look_left", yaw_deg=-90.0),
    "look_right": OcularPromptIntent("look_right", yaw_deg=90.0),
    "look_up": OcularPromptIntent("look_up", pitch_deg=-90.0),
    "look_down": OcularPromptIntent("look_down", pitch_deg=90.0),
    "look_behind_right_eye": OcularPromptIntent("look_behind_right_eye", eye="right", yaw_deg=180.0, requires_depth_projection=True),
    "look_behind_left_eye": OcularPromptIntent("look_behind_left_eye", eye="left", yaw_deg=180.0, requires_depth_projection=True),
    "look_behind_both_eyes": OcularPromptIntent("look_behind_both_eyes", eye="both", yaw_deg=180.0, requires_depth_projection=True),
    "rotate_globe_alignment_positive": OcularPromptIntent("rotate_globe_alignment_positive", alignment_axis_rotation_deg=30.0, requires_depth_projection=True),
    "rotate_globe_alignment_negative": OcularPromptIntent("rotate_globe_alignment_negative", alignment_axis_rotation_deg=-30.0, requires_depth_projection=True),
}

_ALIASES = {
    "look forward": "look_forward", "forward": "look_forward",
    "look left": "look_left", "left": "look_left",
    "look right": "look_right", "right": "look_right",
    "look up": "look_up", "up": "look_up",
    "look down": "look_down", "down": "look_down",
    "look behind with right eye": "look_behind_right_eye",
    "look behind right eye": "look_behind_right_eye",
    "right eye behind": "look_behind_right_eye",
    "look behind with left eye": "look_behind_left_eye",
    "look behind left eye": "look_behind_left_eye",
    "look behind": "look_behind_both_eyes",
    "look behind with both eyes": "look_behind_both_eyes",
    "rotate globe alignment positive": "rotate_globe_alignment_positive",
    "alignment positive": "rotate_globe_alignment_positive",
    "rotate globe alignment negative": "rotate_globe_alignment_negative",
    "alignment negative": "rotate_globe_alignment_negative",
}


def resolve_prompt_intent(text: str) -> OcularPromptIntent:
    """Resolve a stable human-readable ocular phrase without guessing unknown intent."""
    key = " ".join(text.strip().lower().replace("_", " ").split())
    canonical = _ALIASES.get(key, key.replace(" ", "_"))
    try:
        return _INTENTS[canonical]
    except KeyError as exc:
        raise ValueError(f"unknown ocular prompt intent: {text!r}") from exc


def prompt_intent_names() -> tuple[str, ...]:
    """Expose canonical names for prompt/schema tooling without parser coupling."""
    return tuple(sorted(_INTENTS))
