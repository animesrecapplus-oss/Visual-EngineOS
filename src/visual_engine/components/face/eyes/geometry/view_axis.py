from __future__ import annotations

from dataclasses import dataclass
import math

Vec3 = tuple[float, float, float]


def _dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _cross(a: Vec3, b: Vec3) -> Vec3:
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def _norm(v: Vec3) -> float:
    return math.sqrt(_dot(v, v))


def _unit(v: Vec3, *, name: str) -> Vec3:
    n = _norm(v)
    if n <= 1e-12 or not math.isfinite(n):
        raise ValueError(f"{name} must be a finite non-zero vector")
    return (v[0] / n, v[1] / n, v[2] / n)


def rotate_vector(v: Vec3, axis: Vec3, degrees: float) -> Vec3:
    """Rotate a vector with Rodrigues' formula; no Euler-angle accumulation."""
    if not math.isfinite(degrees):
        raise ValueError("rotation degrees must be finite")
    k = _unit(axis, name="rotation axis")
    theta = math.radians(degrees)
    c, s = math.cos(theta), math.sin(theta)
    k_cross_v = _cross(k, v)
    kv = _dot(k, v)
    return (
        v[0] * c + k_cross_v[0] * s + k[0] * kv * (1.0 - c),
        v[1] * c + k_cross_v[1] * s + k[1] * kv * (1.0 - c),
        v[2] * c + k_cross_v[2] * s + k[2] * kv * (1.0 - c),
    )


@dataclass(frozen=True, slots=True)
class OcularPose3D:
    """Independent ocular orientation channels.

    ``roll_deg`` is the historical ``EyeParameters.rotation_deg`` channel.  Yaw
    and pitch change the globe view direction; alignment rotation is a separate
    local-X rotation retained for the V1.10 contract.  The four values are not
    blindly added: they are composed as rotations in a declared order.
    """

    yaw_deg: float = 0.0
    pitch_deg: float = 0.0
    roll_deg: float = 0.0
    alignment_axis_rotation_deg: float = 0.0

    def __post_init__(self) -> None:
        values = (self.yaw_deg, self.pitch_deg, self.roll_deg, self.alignment_axis_rotation_deg)
        if not all(math.isfinite(float(v)) for v in values):
            raise ValueError("ocular orientation values must be finite")
        if not -180.0 <= self.yaw_deg <= 180.0:
            raise ValueError("yaw_deg must be within [-180,180]")
        if not -90.0 <= self.pitch_deg <= 90.0:
            raise ValueError("pitch_deg must be within [-90,90]")
        if not -89.9 <= self.alignment_axis_rotation_deg <= 89.9:
            raise ValueError("alignment_axis_rotation_deg must be within [-89.9,89.9]")


@dataclass(frozen=True, slots=True)
class OcularBasis3D:
    """Right/transverse, up, and view axes in world coordinates."""

    alignment_axis: Vec3
    vertical_axis: Vec3
    view_axis: Vec3

    def __post_init__(self) -> None:
        for name, value in (("alignment_axis", self.alignment_axis), ("vertical_axis", self.vertical_axis), ("view_axis", self.view_axis)):
            _unit(value, name=name)
        if abs(_dot(self.alignment_axis, self.vertical_axis)) > 1e-8:
            raise ValueError("ocular basis alignment/vertical axes are not orthogonal")
        if abs(_dot(self.alignment_axis, self.view_axis)) > 1e-8:
            raise ValueError("ocular basis alignment/view axes are not orthogonal")
        if abs(_dot(self.vertical_axis, self.view_axis)) > 1e-8:
            raise ValueError("ocular basis vertical/view axes are not orthogonal")


def compose_ocular_basis(parent: OcularBasis3D | None = None, pose: OcularPose3D = OcularPose3D()) -> OcularBasis3D:
    """Compose local ocular orientation onto a parent basis.

    The local basis starts as +X alignment, +Y anatomical-up, +Z camera-facing.
    Alignment rotation is applied first, then pitch, yaw and finally roll.  When a
    parent exists, its basis vectors become the axes of the local coordinate frame.
    This preserves hierarchy without pretending Euler angles are commutative.
    """
    if parent is None:
        parent = OcularBasis3D((1.0, 0.0, 0.0), (0.0, 1.0, 0.0), (0.0, 0.0, 1.0))

    x, y, z = parent.alignment_axis, parent.vertical_axis, parent.view_axis
    x = rotate_vector(x, x, pose.alignment_axis_rotation_deg)
    y = rotate_vector(y, parent.alignment_axis, pose.alignment_axis_rotation_deg)
    z = rotate_vector(z, parent.alignment_axis, pose.alignment_axis_rotation_deg)
    y = rotate_vector(y, x, pose.pitch_deg)
    z = rotate_vector(z, x, pose.pitch_deg)
    x = rotate_vector(x, y, pose.yaw_deg)
    z = rotate_vector(z, y, pose.yaw_deg)
    x = rotate_vector(x, z, pose.roll_deg)
    y = rotate_vector(y, z, pose.roll_deg)
    return OcularBasis3D(_unit(x, name="alignment_axis"), _unit(y, name="vertical_axis"), _unit(z, name="view_axis"))


def basis_handedness(basis: OcularBasis3D) -> float:
    """Return the signed determinant-like handedness diagnostic."""
    return _dot(_cross(basis.alignment_axis, basis.vertical_axis), basis.view_axis)
