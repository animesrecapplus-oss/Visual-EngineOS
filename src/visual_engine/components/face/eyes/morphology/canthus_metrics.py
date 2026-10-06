from __future__ import annotations

"""Renderer-neutral measurements for a single cubic canthus bridge.

The module measures an already-resolved bridge; it never changes the geometry.  The
"triangle" diagnostics are evidence signals, not an aesthetic classifier.  Their
purpose is to expose concentrated turning, non-simple tangent travel and excessive
chord deviation so a later geometry brick can be challenged against real references.
"""

import math
from dataclasses import dataclass

Point = tuple[float, float]
Cubic = tuple[Point, Point, Point, Point]
_EPS = 1e-14


@dataclass(frozen=True, slots=True)
class CanthusMetrics:
    """Scale/rotation invariant measurements of one cubic canthus bridge."""

    valid: bool
    chord_length: float
    arc_length: float
    arc_to_chord_ratio: float
    normalized_arc_length: float
    tangent_start_angle_rad: float
    tangent_end_angle_rad: float
    net_turn_angle_rad: float
    total_abs_turning_rad: float
    turning_efficiency: float
    min_speed_ratio: float
    max_curvature: float
    max_curvature_normalized: float
    mean_abs_curvature_normalized: float
    curvature_peak_to_mean: float
    endpoint_curvature_fraction_20: float
    half_turn_window_ratio: float
    max_chord_deviation_ratio: float
    curvature_sign_changes: int
    triangle_evidence: float



def _finite_point(p: Point) -> bool:
    return math.isfinite(p[0]) and math.isfinite(p[1])


def _norm(v: Point) -> float:
    return math.hypot(v[0], v[1])



def _bezier(c: Cubic, t: float) -> Point:
    u = 1.0 - t
    return (
        u**3*c[0][0] + 3*u*u*t*c[1][0] + 3*u*t*t*c[2][0] + t**3*c[3][0],
        u**3*c[0][1] + 3*u*u*t*c[1][1] + 3*u*t*t*c[2][1] + t**3*c[3][1],
    )


def _derivative(c: Cubic, t: float) -> Point:
    u = 1.0 - t
    return (
        3*(u*u*(c[1][0]-c[0][0]) + 2*u*t*(c[2][0]-c[1][0]) + t*t*(c[3][0]-c[2][0])),
        3*(u*u*(c[1][1]-c[0][1]) + 2*u*t*(c[2][1]-c[1][1]) + t*t*(c[3][1]-c[2][1])),
    )


def _second_derivative(c: Cubic, t: float) -> Point:
    u = 1.0 - t
    return (
        6*(u*(c[2][0]-2*c[1][0]+c[0][0]) + t*(c[3][0]-2*c[2][0]+c[1][0])),
        6*(u*(c[2][1]-2*c[1][1]+c[0][1]) + t*(c[3][1]-2*c[2][1]+c[1][1])),
    )


def _curvature(c: Cubic, t: float) -> float:
    d = _derivative(c, t)
    dd = _second_derivative(c, t)
    speed = _norm(d)
    if speed <= _EPS:
        return math.nan
    return (d[0]*dd[1] - d[1]*dd[0]) / speed**3


def _gauss_legendre_128() -> tuple[tuple[float, ...], tuple[float, ...]]:
    """Build deterministic 128-point Gauss-Legendre nodes on [0,1]."""
    nodes, weights = [], []
    for k in range(1, 65):
        z = math.cos(math.pi * (k - .25) / 128.5)
        for _ in range(16):
            p0, p1 = 1.0, z
            for degree in range(2, 129):
                p0, p1 = p1, ((2*degree-1)*z*p1-(degree-1)*p0)/degree
            derivative = 128.0 * (z*p1-p0) / (z*z-1.0)
            delta = p1 / derivative
            z -= delta
            if abs(delta) <= 1e-16:
                break
        x = (1.0-z)/2.0
        w = 1.0 / ((1.0-z*z) * derivative*derivative)
        nodes.extend((x, 1.0-x)); weights.extend((w, w))
    return tuple(nodes), tuple(weights)


_GL_NODES, _GL_WEIGHTS = _gauss_legendre_128()


def _integrate_pair(c: Cubic) -> tuple[float, float]:
    """Integrate arc length and absolute curvature with the same 128 nodes."""
    arc = total_turn = 0.0
    for t, weight in zip(_GL_NODES, _GL_WEIGHTS):
        d = _derivative(c, t)
        speed = _norm(d)
        if speed <= _EPS:
            raise ValueError("canthus curve has a zero-speed quadrature point")
        dd = _second_derivative(c, t)
        numerator = d[0]*dd[1] - d[1]*dd[0]
        arc += weight * speed
        total_turn += weight * abs(numerator) / (speed*speed)
    return arc, total_turn


def _local_angle(v: Point, axis: Point, normal: Point) -> float:
    return math.atan2(v[0]*normal[0] + v[1]*normal[1], v[0]*axis[0] + v[1]*axis[1])


def _short_angle(angle: float) -> float:
    return (angle + math.pi) % (2.0*math.pi) - math.pi


def _distribution(c: Cubic, samples: int) -> tuple[float, float, float, int]:
    points = tuple(_bezier(c, i/(samples-1)) for i in range(samples))
    lengths = tuple(_norm((points[i+1][0]-points[i][0], points[i+1][1]-points[i][1])) for i in range(samples-1))
    total_len = sum(lengths)
    curvatures = tuple(_curvature(c, i/(samples-1)) for i in range(samples))
    if any(not math.isfinite(k) for k in curvatures):
        raise ValueError("canthus curve contains a zero-speed sample")
    weights = tuple(0.5*(abs(curvatures[i])+abs(curvatures[i+1]))*lengths[i] for i in range(samples-1))
    total = sum(weights)
    if total <= _EPS:
        return 0.0, 1.0, 0.0, 0
    distances = [0.0]
    for length in lengths:
        distances.append(distances[-1] + length)
    arc_window = 0.20 * total_len
    endpoint = sum(weight for i, weight in enumerate(weights)
                    if distances[i] <= arc_window or distances[i+1] >= total_len-arc_window)
    # Smallest sampled arc interval carrying half the absolute turning.
    target = 0.50 * total
    best = total_len
    j = 0
    running = 0.0
    for i, weight in enumerate(weights):
        running += weight
        while j <= i and running - weights[j] >= target:
            running -= weights[j]
            j += 1
        if running >= target:
            best = min(best, distances[i+1] - distances[j])
    return endpoint / total, best / total_len, max(abs(k) for k in curvatures), _sign_changes(curvatures)


def _sign_changes(values: tuple[float, ...]) -> int:
    signs = []
    scale = max(1.0, max(abs(v) for v in values))
    for value in values:
        if abs(value) <= 1e-10 * scale:
            continue
        sign = 1 if value > 0 else -1
        if not signs or signs[-1] != sign:
            signs.append(sign)
    return max(0, len(signs)-1)


def measure_canthus(
    bridge: Cubic,
    inner: Point,
    outer: Point,
    *,
    samples: int = 257,
) -> CanthusMetrics:
    """Measure a bridge in the same invariant eye frame used by EnvelopeMetrics.

    ``samples`` controls only distribution diagnostics. Arc length and total curvature
    use fixed 128-point Gauss-Legendre quadrature. This distinction is intentional:
    changing diagnostic sampling density does not redefine the primary integrals.
    """
    if samples < 33 or samples % 2 == 0:
        raise ValueError("canthus diagnostic samples must be odd and >= 33")
    if len(bridge) != 4 or not all(_finite_point(p) for p in (*bridge, inner, outer)):
        raise ValueError("canthus bridge and semantic canthi must be finite cubic points")
    dx, dy = outer[0]-inner[0], outer[1]-inner[1]
    width = math.hypot(dx, dy)
    if width <= _EPS or not math.isfinite(width):
        raise ValueError("semantic canthi must define a non-zero eye axis")
    axis = (dx/width, dy/width)
    normal = (-axis[1], axis[0])
    chord = math.dist(bridge[0], bridge[3])
    if chord <= _EPS or not math.isfinite(chord):
        raise ValueError("canthus bridge endpoints must define a non-zero chord")
    start_d, end_d = _derivative(bridge, 0.0), _derivative(bridge, 1.0)
    min_speed = min(_norm(_derivative(bridge, i/(samples-1))) for i in range(samples))
    if min_speed <= _EPS:
        raise ValueError("canthus bridge contains a zero-speed point")
    arc, total_turn = _integrate_pair(bridge)
    start_angle = _local_angle(start_d, axis, normal)
    end_angle = _local_angle(end_d, axis, normal)
    net_turn = _short_angle(end_angle-start_angle)
    efficiency = min(1.0, abs(net_turn)/total_turn) if total_turn > _EPS else 1.0
    endpoint_fraction, half_window, peak, sign_changes = _distribution(bridge, samples)
    # Maximum perpendicular distance from the endpoint chord is the geometric
    # "third-side" evidence of a triangular closure. It is normalized by chord.
    chord_axis = ((bridge[3][0]-bridge[0][0])/chord, (bridge[3][1]-bridge[0][1])/chord)
    chord_normal = (-chord_axis[1], chord_axis[0])
    deviation = max(abs(((_bezier(bridge, i/(samples-1))[0]-bridge[0][0])*chord_normal[0]
                          + (_bezier(bridge, i/(samples-1))[1]-bridge[0][1])*chord_normal[1]))
                    for i in range(samples)) / chord
    mean_normalized = width * total_turn / arc
    peak_normalized = width * peak
    peak_to_mean = peak_normalized / mean_normalized if mean_normalized > _EPS else 0.0
    # Diagnostic score: all ingredients are dimensionless and monotonic. No score
    # is accepted as a reference truth; 0.75 is only a deliberately conservative
    # flag threshold until reference curves are formally calibrated.
    concentration = min(1.0, endpoint_fraction)
    spike = min(1.0, max(0.0, (peak_to_mean-1.0) / 9.0))
    non_simple = min(1.0, max(0.0, (1.0-efficiency) / 0.75))
    deviation_term = min(1.0, max(0.0, deviation / 0.10))
    triangle_evidence = (concentration * spike * (0.5 + 0.5*non_simple) * (0.5 + 0.5*deviation_term)) ** 0.25
    valid = all(math.isfinite(v) for v in (arc, total_turn, efficiency, min_speed, peak, mean_normalized, peak_to_mean, deviation, triangle_evidence))
    return CanthusMetrics(
        valid=valid, chord_length=chord, arc_length=arc, arc_to_chord_ratio=arc/chord,
        normalized_arc_length=arc/width, tangent_start_angle_rad=start_angle,
        tangent_end_angle_rad=end_angle, net_turn_angle_rad=net_turn,
        total_abs_turning_rad=total_turn, turning_efficiency=efficiency,
        min_speed_ratio=min_speed/(arc), max_curvature=peak, max_curvature_normalized=width*peak,
        mean_abs_curvature_normalized=mean_normalized, curvature_peak_to_mean=peak_to_mean,
        endpoint_curvature_fraction_20=endpoint_fraction, half_turn_window_ratio=half_window,
        max_chord_deviation_ratio=deviation, curvature_sign_changes=sign_changes,
        triangle_evidence=triangle_evidence,
    )
