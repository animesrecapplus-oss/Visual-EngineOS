from __future__ import annotations

from typing import Literal

Point = tuple[float, float]
TerminalMode = Literal["shared_point", "bridge"]


def resolve_terminal_points(
    upper: Point,
    lower: Point,
    mode: TerminalMode,
) -> tuple[Point, Point]:
    """Resolve a semantic lid terminal without inventing a visible cap.

    ``shared_point`` collapses the two margin endpoints to their midpoint.  This
    is intentionally a topological terminal, not a rendered stroke.  ``bridge``
    preserves the finite-gap V1.4-V1.6 geometry for explicit legacy authoring.
    """
    if mode == "bridge":
        return upper, lower
    if mode != "shared_point":
        raise ValueError(f"unknown canthus terminal mode: {mode}")
    midpoint = ((upper[0] + lower[0]) * 0.5, (upper[1] + lower[1]) * 0.5)
    return midpoint, midpoint
