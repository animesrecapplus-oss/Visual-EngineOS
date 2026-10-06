from __future__ import annotations

import math

Point = tuple[float, float]


def project_alignment_axis(point: Point, alignment_axis_rotation_deg: float) -> Point:
    """Project a planar ocular surface after rotation about its alignment axis.

    The alignment axis is the local X axis (the axis running from one eye toward
    the other in a bilateral face). A 3D rotation about that axis changes the
    visible Y extent by foreshortening under the current orthographic renderer.
    This is intentionally separate from ``rotation_deg``, which is the 2D roll
    around the view axis. The two operations can therefore be composed without
    conflating roll with depth-axis orientation.
    """
    if not math.isfinite(alignment_axis_rotation_deg):
        raise ValueError("alignment_axis_rotation_deg must be finite")
    c = math.cos(math.radians(alignment_axis_rotation_deg))
    return point[0], point[1] * c




def face_local_to_world(point: Point, *, roll_deg: float) -> Point:
    """Place face-owned 2D geometry without applying ocular alignment depth.

    Lid margins, canthi, orbital aperture and facial folds live in the parent face
    frame. They inherit screen roll, but not the independent 3D rotation of the
    eyeball. This distinction is the core V1.17 alignment/globe decoupling rule.
    """
    if not math.isfinite(roll_deg):
        raise ValueError("roll_deg must be finite")
    a = math.radians(roll_deg)
    c, s = math.cos(a), math.sin(a)
    x, y = point
    return c * x - s * y, s * x + c * y

def ocular_local_to_world(point: Point, *, roll_deg: float, alignment_axis_rotation_deg: float) -> Point:
    """Apply alignment-axis projection first, then the established 2D roll.

    This order represents a local ocular surface rotated in depth and then placed
    in the image plane. It is a renderer-neutral 2.5D approximation, not a claim
    that the current engine is a full eyeball/3D head renderer.
    """
    x, y = project_alignment_axis(point, alignment_axis_rotation_deg)
    a = math.radians(roll_deg)
    c, s = math.cos(a), math.sin(a)
    return c * x - s * y, s * x + c * y


def project_ellipse_axes(rx: float, ry: float, *, alignment_axis_rotation_deg: float, roll_deg: float) -> tuple[float, float, float]:
    """Return projected ellipse radii and world orientation.

    The input ellipse is axis-aligned in the anatomical frame. Applying the
    alignment-axis projection followed by roll is a linear transform; the result
    is decomposed into principal radii/orientation so SVG can render it faithfully.
    """
    if rx <= 0 or ry <= 0 or not all(math.isfinite(v) for v in (rx, ry, alignment_axis_rotation_deg, roll_deg)):
        raise ValueError("ellipse dimensions and orientation must be finite and positive")
    # Columns of the linear map applied to the ellipse's local basis vectors.
    c_align = math.cos(math.radians(alignment_axis_rotation_deg))
    a = math.radians(roll_deg)
    c, s = math.cos(a), math.sin(a)
    m00, m01 = c * rx, -s * c_align * ry
    m10, m11 = s * rx, c * c_align * ry
    # Singular values of the 2x2 matrix give the projected principal radii.
    # M M^T is the world-space covariance of the transformed ellipse. Using
    # M^T M here would return the orientation in the source frame, which is the
    # subtle error that makes a rotated projected iris render axis-aligned.
    q00 = m00 * m00 + m01 * m01
    q01 = m00 * m10 + m01 * m11
    q11 = m10 * m10 + m11 * m11
    trace = q00 + q11
    disc = max(0.0, (q00 - q11) ** 2 + 4.0 * q01 * q01)
    lam_major = max(0.0, 0.5 * (trace + math.sqrt(disc)))
    lam_minor = max(0.0, 0.5 * (trace - math.sqrt(disc)))
    major, minor = math.sqrt(lam_major), math.sqrt(lam_minor)
    if major <= 1e-15:
        return 0.0, 0.0, 0.0
    if abs(q01) > 1e-12 or abs(q00 - lam_major) > 1e-12:
        vx, vy = q01, lam_major - q00
        norm = math.hypot(vx, vy)
        orientation = math.degrees(math.atan2(vy / norm, vx / norm)) if norm > 1e-15 else 0.0
    else:
        orientation = 0.0 if q00 >= q11 else 90.0
    return major, minor, orientation
