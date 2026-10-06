from __future__ import annotations

import math

from ..morphology.spec import EyeParameters
from .shape import _rotate
from .curve import _bezier
from .canthus import build_canthus_endpoints
from .canthus_profile import apply_endpoint_profile
from .terminal import resolve_terminal_points

def _contour(p: EyeParameters, half_w: float, half_h: float, opening: float, *, mirror_x: bool = False) -> tuple[tuple[float, float], ...]:
    """Build sampled lid margins with local endpoint ownership.

    Interior curvature is generated from nominal dimensions; the four canthus
    endpoints are then injected explicitly. Consequently a corner parameter
    cannot alter the opposite corner's endpoint or internal ocular assembly.
    The gaze-safe continuity layer consumes the resulting samples.
    """
    n_half = max(8, p.contour_samples // 2)
    def orient(x: float, y: float) -> tuple[float, float]:
        return _rotate(-x if mirror_x else x, y, p.rotation_deg)

    if p.shape in {"round", "large_round"}:
        radius = half_w
        vertical_scale = 0.35 + 0.65 * opening
        upper, lower = [], []
        for i in range(n_half):
            u = i / (n_half - 1)
            theta = math.pi - math.pi * u
            x = radius * math.cos(theta)
            y = -radius * math.sin(theta) * vertical_scale
            upper.append(orient(x, y))
            lower.append(orient(x, -y))
        canthi = build_canthus_endpoints(
            half_w, half_h,
            inner_roundness=p.effective_canthus_inner_roundness,
            outer_roundness=p.effective_canthus_outer_roundness,
        )
        upper[0], upper[-1] = orient(*canthi.inner_upper), orient(*canthi.outer_upper)
        lower[0], lower[-1] = orient(*canthi.inner_lower), orient(*canthi.outer_lower)
        _resolve_terminal_pair(upper, lower, p)
        _enforce_canthus_tangents(
            upper, (p.canthus_inner_upper_profile, p.canthus_outer_upper_profile),
            lower, (p.canthus_inner_lower_profile, p.canthus_outer_lower_profile),
            p_transition_inner=p.canthus_inner_transition,
            p_transition_outer=p.canthus_outer_transition,
            inner_mode=p.canthus_inner_terminal.mode, outer_mode=p.canthus_outer_terminal.mode,
            opening=opening,
        )
        return tuple(upper + list(reversed(lower)))
    shape_upper = {"almond": 1.0, "round": 1.00, "large_round": 1.00, "ellipse": 1.00, "narrow": .58, "droopy": .82, "sharp": .78, "upturned": .92, "downturned": .92}[p.shape]
    shape_lower = {"almond": .88, "round": 1.00, "large_round": 1.00, "ellipse": .88, "narrow": .52, "droopy": .72, "sharp": .70, "upturned": .88, "downturned": .88}[p.shape]
    upper_h = half_h * shape_upper * p.upper_curve * (0.35 + 0.65 * opening)
    lower_h = half_h * shape_lower * p.lower_curve * (0.35 + 0.65 * opening)
    right_bias = (-0.12 if p.shape == "upturned" else 0.12 if p.shape == "downturned" else 0.0) * half_h * opening
    canthi = build_canthus_endpoints(
        half_w, half_h,
        inner_roundness=p.effective_canthus_inner_roundness,
        outer_roundness=p.effective_canthus_outer_roundness,
    )
    left_upper, left_lower = canthi.inner_upper, canthi.inner_lower
    right_upper, right_lower = canthi.outer_upper, canthi.outer_lower
    upper, lower = [], []
    for i in range(n_half):
        u = i / (n_half - 1)
        # Local endpoint controls keep the opposite canthus independent.
        up_c1 = (-half_w * .78, -upper_h * .72)
        up_c2 = (half_w * .78, -upper_h * .72 + right_bias)
        lo_c1 = (-half_w * .78, lower_h * .70)
        lo_c2 = (half_w * .78, lower_h * .70 + right_bias)
        ub = _bezier((-half_w, 0.0), up_c1, up_c2, (half_w, 0.0), u)
        lb = _bezier((-half_w, 0.0), lo_c1, lo_c2, (half_w, 0.0), u)
        if i == 0:
            ub, lb = left_upper, left_lower
        elif i == n_half - 1:
            ub, lb = right_upper, right_lower
        # Zero-value endpoint window prevents contour variation from changing
        # canthus coordinates or endpoint tangents.
        window = math.sin(math.pi * u) ** 2
        wave = p.contour_wave_amplitude * math.sin(p.contour_wave_frequency * math.pi * u) * window
        irr = p.contour_irregularity * 0.025 * math.sin(3.0 * math.pi * u + .7) * window
        x_skew = p.asymmetry * 0.035 * half_w * math.sin(math.pi * u)
        delta = (wave + irr) * min(half_w, max(half_h, 1e-9))
        ux, uy = orient(ub[0] + x_skew, ub[1] - delta)
        lx, ly = orient(lb[0] + x_skew, lb[1] + delta)
        upper.append((ux, uy)); lower.append((lx, ly))
    _resolve_terminal_pair(upper, lower, p)
    _enforce_canthus_tangents(
        upper, (p.canthus_inner_upper_profile, p.canthus_outer_upper_profile),
        lower, (p.canthus_inner_lower_profile, p.canthus_outer_lower_profile),
        p_transition_inner=p.canthus_inner_transition,
        p_transition_outer=p.canthus_outer_transition,
        inner_mode=p.canthus_inner_terminal.mode, outer_mode=p.canthus_outer_terminal.mode,
    )
    return tuple(upper + list(reversed(lower)))


def _resolve_terminal_pair(upper, lower, p: EyeParameters) -> None:
    """Apply V1.7 terminal topology after endpoint ownership is resolved."""
    iu, il = resolve_terminal_points(upper[0], lower[0], p.canthus_inner_terminal.mode)
    ou, ol = resolve_terminal_points(upper[-1], lower[-1], p.canthus_outer_terminal.mode)
    upper[0], lower[0] = iu, il
    upper[-1], lower[-1] = ou, ol


def _enforce_canthus_tangents(
    upper: list[tuple[float, float]], upper_profile, lower: list[tuple[float, float]],
    lower_profile, *, p_transition_inner: float = 0.0, p_transition_outer: float = 0.0,
    inner_mode: str = "bridge", outer_mode: str = "bridge", opening: float = 1.0,
) -> None:
    """Apply V1.5 baseline handles plus optional V1.6 four-endpoint profiles.

    The four endpoint profiles are deliberately applied independently:
    ``inner_upper``, ``inner_lower``, ``outer_upper`` and ``outer_lower``.  This
    avoids the V1.5 coupling in which one inner scalar necessarily changed both
    lid junctions in the same way.  The endpoint coordinates remain semantic
    anchors and the downstream bridge still derives its C1 derivatives from the
    same samples.
    """
    if len(upper) < 3 or len(lower) < 3:
        return
    if not all(math.isfinite(v) and 0.0 <= v <= 1.0 for v in (p_transition_inner, p_transition_outer)):
        raise ValueError("canthus transition must be finite and within [0,1]")

    def unit(dx: float, dy: float) -> tuple[float, float]:
        norm = math.hypot(dx, dy)
        if norm <= 1e-15:
            return 1.0, 0.0
        return dx / norm, dy / norm

    def baseline_handle(p0, p2, gap, transition, mode):
        dx, dy = p2[0] - p0[0], p2[1] - p0[1]
        ux, uy = unit(dx, dy)
        # V1.5 remains the baseline. V1.6 modifies that baseline only through
        # explicit endpoint profiles, so a default profile is bit-for-bit
        # equivalent to the previous geometry.
        local_cap = math.hypot(dx, dy) * (0.5 + 0.4 * transition)
        if mode == "shared_point":
            # A shared terminal has no finite bridge gap. Preserve a useful lid
            # tangent by using the local sampling scale instead of a near-zero
            # bridge handle; this is a terminal convergence contract, not a cap.
            return math.hypot(dx, dy) * 0.25 * max(opening, 0.05)
        gap_target = gap * (0.45 + 0.75 * transition)
        return min(local_cap, max(gap_target, 1e-15))

    inner_gap = math.hypot(lower[0][0] - upper[0][0], lower[0][1] - upper[0][1])
    uh = baseline_handle(upper[0], upper[2], inner_gap, p_transition_inner, inner_mode)
    lh = baseline_handle(lower[0], lower[2], inner_gap, p_transition_inner, inner_mode)
    apply_endpoint_profile(upper, at_end=False, baseline_handle=uh, profile=upper_profile[0])
    apply_endpoint_profile(lower, at_end=False, baseline_handle=lh, profile=lower_profile[0])

    outer_gap = math.hypot(lower[-1][0] - upper[-1][0], lower[-1][1] - upper[-1][1])
    uh = baseline_handle(upper[-1], upper[-3], outer_gap, p_transition_outer, outer_mode)
    lh = baseline_handle(lower[-1], lower[-3], outer_gap, p_transition_outer, outer_mode)
    apply_endpoint_profile(upper, at_end=True, baseline_handle=uh, profile=upper_profile[1])
    apply_endpoint_profile(lower, at_end=True, baseline_handle=lh, profile=lower_profile[1])


def _bounds(points: tuple[tuple[float, float], ...]) -> tuple[float, float, float, float]:
    xs = [x for x, _ in points]; ys = [y for _, y in points]
    return min(xs), max(xs), min(ys), max(ys)
