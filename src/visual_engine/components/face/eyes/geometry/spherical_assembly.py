from __future__ import annotations

from dataclasses import dataclass
import math

from .projection3d import Camera3D, Point2, project_point, project_sphere_silhouette, projected_ellipse_rotation
from .view_axis import OcularBasis3D, OcularPose3D, Vec3, compose_ocular_basis
from .surface_samples import project_spherical_patch_samples
from .alignment_coupling import AlignmentCouplingReport, resolve_alignment_coupling


def _dot(a: Vec3, b: Vec3) -> float:
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _norm(v: Vec3) -> float:
    return math.sqrt(_dot(v, v))


def _unit(v: Vec3, name: str = "vector") -> Vec3:
    n = _norm(v)
    if n <= 1e-12 or not math.isfinite(n):
        raise ValueError(f"{name} must be finite and non-zero")
    return tuple(x / n for x in v)


def _add(a: Vec3, b: Vec3) -> Vec3:
    return a[0] + b[0], a[1] + b[1], a[2] + b[2]


def _scale(a: Vec3, s: float) -> Vec3:
    return a[0] * s, a[1] * s, a[2] * s


@dataclass(frozen=True, slots=True)
class SurfaceAttachment:
    """A child surface frame attached to the same spherical parent as its owner."""

    center: Vec3
    normal: Vec3
    tangent_x: Vec3
    tangent_y: Vec3


@dataclass(frozen=True, slots=True)
class SurfaceVisibility:
    near_canthus: str
    far_canthus: str
    iris: str
    pupil: str
    sclera: str
    cornea: str


@dataclass(frozen=True, slots=True)
class SphericalEyeAssembly:
    center: Vec3
    radius: float
    basis: OcularBasis3D
    sclera_silhouette: tuple[Point2, ...]
    cornea_outline: tuple[Point2, ...]
    iris_outline: tuple[Point2, ...]
    pupil_outline: tuple[Point2, ...]
    visibility: SurfaceVisibility
    iris_surface_center: Vec3
    pupil_surface_center: Vec3
    # V1.14 explicit parent-child attachment frames. Pupil children are never
    # recomputed from the eye origin after the iris has moved.
    iris_attachment: SurfaceAttachment | None = None
    pupil_attachments: tuple[SurfaceAttachment, ...] = ()
    pupil_outlines: tuple[tuple[Point2, ...], ...] = ()
    pupil_projection_rotations: tuple[float, ...] = ()
    iris_projection_rotation: float = 0.0
    iris_projected_center: Point2 | None = None
    pupil_projected_centers: tuple[Point2, ...] = ()
    cornea_attachment: SurfaceAttachment | None = None
    # Fraction of projected child samples inside the actual eyelid aperture.
    iris_aperture_fraction: float = 1.0
    pupil_aperture_fractions: tuple[float, ...] = ()
    eyelid_coupling: object | None = None
    # V1.15 keeps 3D samples beside their 2D projections so depth tests never
    # have to reconstruct a child position from a bounding box.
    iris_surface_samples: tuple[Vec3, ...] = ()
    pupil_surface_samples: tuple[tuple[Vec3, ...], ...] = ()
    depth_occlusion: object | None = None
    alignment_coupling: AlignmentCouplingReport | None = None


def _surface_attachment(
    center: Vec3,
    radius: float,
    basis: OcularBasis3D,
    offset_x: float,
    offset_y: float,
) -> SurfaceAttachment:
    """Place a point on the front sphere using the eye-local tangent coordinates.

    The old V1.13 implementation placed the pupil with an absolute radial distance
    of ``1.01``. That was dimensionally wrong for a globe whose radius was often
    ``0.5`` and was the direct cause of the visible pupil/iris separation. Here the
    pupil is a child offset from the already-resolved iris frame.
    """
    if not all(math.isfinite(v) for v in (offset_x, offset_y, radius)):
        raise ValueError("surface offsets must be finite")
    offset_length = math.hypot(offset_x, offset_y)
    max_offset = radius * 0.94
    if offset_length >= max_offset:
        if offset_length <= 1e-12:
            raise ValueError("surface child offset is degenerate")
        scale = max_offset / offset_length
        offset_x *= scale
        offset_y *= scale
    radial_sq = radius * radius - offset_x * offset_x - offset_y * offset_y
    if radial_sq <= 1e-12:
        raise ValueError("surface child offset lies on or beyond the globe rim")
    z = math.sqrt(radial_sq)
    radial = _add(_scale(basis.alignment_axis, offset_x), _scale(basis.vertical_axis, offset_y))
    radial = _add(radial, _scale(basis.view_axis, z))
    normal = _unit(radial, "surface normal")
    point = _add(center, radial)
    # Tangent axes are projected parent axes with their normal component removed.
    tx = _unit(_add(basis.alignment_axis, _scale(normal, -_dot(basis.alignment_axis, normal))), "surface tangent_x")
    ty = _unit(_add(basis.vertical_axis, _scale(normal, -_dot(basis.vertical_axis, normal))), "surface tangent_y")
    return SurfaceAttachment(point, normal, tx, ty)


def _child_attachment(parent: SurfaceAttachment, center: Vec3, radius: float, dx: float, dy: float) -> SurfaceAttachment:
    """Move an ocular child along the parent's tangent plane, then re-project to the sphere."""
    raw = _add(parent.center, _add(_scale(parent.tangent_x, dx), _scale(parent.tangent_y, dy)))
    radial = (raw[0]-center[0], raw[1]-center[1], raw[2]-center[2])
    normal = _unit(radial, "child surface normal")
    point = _add(center, _scale(normal, radius))
    tx = _unit(_add(parent.tangent_x, _scale(normal, -_dot(parent.tangent_x, normal))), "child tangent_x")
    ty = _unit(_add(parent.tangent_y, _scale(normal, -_dot(parent.tangent_y, normal))), "child tangent_y")
    return SurfaceAttachment(point, normal, tx, ty)


def _visibility(normal: Vec3, camera_forward: Vec3) -> str:
    d = _dot(normal, camera_forward)
    if d <= 1e-8:
        return "hidden"
    if d < 0.25:
        return "partially_visible"
    return "visible"


def build_spherical_eye_assembly(
    *,
    center: Vec3 = (0.0, 0.0, 0.0),
    radius: float = 0.5,
    pose: OcularPose3D = OcularPose3D(),
    parent_basis: OcularBasis3D | None = None,
    iris_radius: float | None = None,
    pupil_radius: float | None = None,
    cornea_radius: float | None = None,
    camera: Camera3D = Camera3D(),
    samples: int = 96,
    iris_offset_local: tuple[float, float] = (0.0, 0.0),
    pupil_offsets_local: tuple[tuple[float, float], ...] = (),
    pupil_radii: tuple[float, ...] = (),
    aperture_polygon: tuple[Point2, ...] = (),
    eyelid_coupling: object | None = None,
) -> SphericalEyeAssembly:
    """Build the V1.14 spherical parent/child ocular assembly.

    ``iris_offset_local`` moves the iris on the globe. Every pupil offset is then
    interpreted in the iris tangent frame, so moving the iris necessarily moves
    its pupil children. The eyelid aperture is passed separately and never mutated.
    """
    if radius <= 0 or not math.isfinite(radius):
        raise ValueError("radius must be finite and > 0")
    for value, name in ((iris_radius, "iris_radius"), (pupil_radius, "pupil_radius"), (cornea_radius, "cornea_radius")):
        if value is not None and (value <= 0 or not math.isfinite(value)):
            raise ValueError(f"{name} must be finite and > 0")
    iris_r = iris_radius if iris_radius is not None else radius * 0.26
    default_pupil_r = pupil_radius if pupil_radius is not None else iris_r * 0.38
    cornea_r = cornea_radius if cornea_radius is not None else radius * 0.31
    if default_pupil_r >= iris_r or iris_r >= radius:
        raise ValueError("pupil < iris < globe radius invariant violated")
    if pupil_radii and any(r <= 0 or r >= iris_r or not math.isfinite(r) for r in pupil_radii):
        raise ValueError("pupil radii must satisfy 0 < radius < iris radius")
    basis = compose_ocular_basis(parent_basis, pose)
    alignment_coupling = resolve_alignment_coupling(parent_basis=parent_basis, alignment_deg=pose.alignment_axis_rotation_deg)
    camera_forward = (0.0, 0.0, 1.0)
    iris_attachment = _surface_attachment(center, radius, basis, iris_offset_local[0], iris_offset_local[1])
    iris_visible = _visibility(iris_attachment.normal, camera_forward)
    sclera = project_sphere_silhouette(center, radius, camera, samples=samples)
    empty: tuple[Point2, ...] = ()
    if iris_visible == "hidden":
        return SphericalEyeAssembly(
            center=center, radius=radius, basis=basis, sclera_silhouette=sclera,
            cornea_outline=empty, iris_outline=empty, pupil_outline=empty,
            visibility=SurfaceVisibility("visible", "visible", "hidden", "hidden", "visible", "hidden"),
            iris_surface_center=iris_attachment.center, pupil_surface_center=iris_attachment.center,
            iris_attachment=iris_attachment, iris_projected_center=project_point(iris_attachment.center, camera),
            eyelid_coupling=eyelid_coupling, alignment_coupling=alignment_coupling,
            iris_surface_samples=(), pupil_surface_samples=(),
        )
    iris, iris_surface_samples = project_spherical_patch_samples(iris_attachment, min(iris_r, radius * .92), radius, camera, samples)
    cornea_attachment = iris_attachment
    cornea, _cornea_surface_samples = project_spherical_patch_samples(cornea_attachment, min(cornea_r, radius * .95), radius, camera, samples)
    offsets = pupil_offsets_local or ((0.0, 0.0),)
    radii = pupil_radii or tuple(default_pupil_r for _ in offsets)
    pupil_attachments = []
    pupil_outlines = []
    pupil_surface_samples = []
    for (dx, dy), pr in zip(offsets, radii):
        max_offset = max(0.0, iris_r - pr) * 0.98
        length = math.hypot(dx, dy)
        if length > max_offset and length > 0:
            scale = max_offset / length
            dx, dy = dx * scale, dy * scale
        attachment = _child_attachment(iris_attachment, center, radius, dx, dy)
        pupil_attachments.append(attachment)
        pupil_outline, pupil_points3 = project_spherical_patch_samples(attachment, min(pr, radius * .90), radius, camera, max(48, samples // 2))
        pupil_outlines.append(pupil_outline)
        pupil_surface_samples.append(pupil_points3)
    pupil = pupil_outlines[0] if pupil_outlines else empty
    pupil_rotations = tuple(projected_ellipse_rotation(outline) for outline in pupil_outlines)
    iris_rotation = projected_ellipse_rotation(iris)
    iris_projected_center = project_point(iris_attachment.center, camera)
    pupil_projected_centers = tuple(project_point(a.center, camera) for a in pupil_attachments)
    d = max(0.0, min(1.0, _dot(iris_attachment.normal, camera_forward)))
    visibility = SurfaceVisibility(
        near_canthus="visible" if d >= .25 else "partially_visible",
        far_canthus="visible" if d >= .6 else "partially_visible",
        iris=iris_visible,
        pupil="visible" if d >= .15 else "partially_visible",
        sclera="visible",
        cornea="visible" if d >= .1 else "partially_visible",
    )
    return SphericalEyeAssembly(
        center=center, radius=radius, basis=basis, sclera_silhouette=sclera,
        cornea_outline=cornea, iris_outline=iris, pupil_outline=pupil,
        visibility=visibility, iris_surface_center=iris_attachment.center,
        pupil_surface_center=pupil_attachments[0].center if pupil_attachments else iris_attachment.center,
        iris_attachment=iris_attachment, pupil_attachments=tuple(pupil_attachments),
        pupil_outlines=tuple(pupil_outlines), pupil_projection_rotations=pupil_rotations,
        iris_projection_rotation=iris_rotation, iris_projected_center=iris_projected_center,
        pupil_projected_centers=pupil_projected_centers, cornea_attachment=cornea_attachment,
        eyelid_coupling=eyelid_coupling, alignment_coupling=alignment_coupling,
        iris_surface_samples=tuple(iris_surface_samples), pupil_surface_samples=tuple(pupil_surface_samples),
    )
