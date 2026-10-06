from __future__ import annotations

from ..appearance.spec import EyeAppearance
from ..morphology.spec import EyeParameters
from .containment import _clamp_to_iris
from .orientation import ocular_local_to_world, project_ellipse_axes




def resolve_pupil_child_offsets_local(
    params: EyeParameters,
    appearance: EyeAppearance,
    *,
    assembly_local: tuple[float, float],
    iris_rx: float,
    iris_ry: float,
    reference_width: float,
    reference_height: float,
) -> tuple[tuple[float, float], ...]:
    """Resolve pupil positions as offsets from the already-resolved iris parent.

    This is the single source for the pupil attachment contract. A pupil may have
    an authored local offset, but that offset is always relative to the current
    iris assembly; it is never recomputed from the eye origin after gaze/yaw moves
    the iris.
    """
    offsets: list[tuple[float, float]] = []
    for spec in appearance.pupils:
        sx = params.pupil_offset_x * reference_width * .5 + spec.x * reference_width * .5
        sy = params.pupil_offset_y * reference_height * .5 + spec.y * reference_height * .5
        if abs(sx) > 1e-12 or abs(sy) > 1e-12:
            cx, cy = _clamp_to_iris(assembly_local[0] + sx, assembly_local[1] + sy, assembly_local, iris_rx, iris_ry, 0.0)
            sx, sy = cx - assembly_local[0], cy - assembly_local[1]
        offsets.append((sx, sy))
    return tuple(offsets)


def build_projected_internal_assembly(
    params: EyeParameters,
    appearance: EyeAppearance,
    *,
    center: tuple[float, float],
    assembly_local: tuple[float, float],
    iris_rx: float,
    iris_ry: float,
    reference_width: float,
    reference_height: float,
) -> tuple[tuple[tuple[float, float], ...], tuple[tuple[float, float], ...], tuple[float, ...], tuple[float, float], tuple[float, float], float, tuple[float, float], float, float, float]:
    """Project iris, pupil and reflection children through one ocular orientation.

    All child centers originate in the same canonical eye-local frame. The parent
    alignment-axis projection and roll are applied once here, preventing the common
    failure mode where the sclera rotates but the iris/pupil/reflection remain flat.
    """
    iris_offset = ocular_local_to_world(
        assembly_local, roll_deg=params.rotation_deg,
        alignment_axis_rotation_deg=params.alignment_axis_rotation_deg,
    )
    iris_center = (center[0] + iris_offset[0], center[1] + iris_offset[1])
    iris_rx_p, iris_ry_p, iris_rot = project_ellipse_axes(
        iris_rx, iris_ry,
        alignment_axis_rotation_deg=params.alignment_axis_rotation_deg,
        roll_deg=params.rotation_deg,
    )
    pupil_centers: list[tuple[float, float]] = []
    pupil_radii: list[tuple[float, float]] = []
    pupil_rotations: list[float] = []
    child_offsets = resolve_pupil_child_offsets_local(
        params, appearance, assembly_local=assembly_local, iris_rx=iris_rx, iris_ry=iris_ry,
        reference_width=reference_width, reference_height=reference_height,
    )
    for spec, (sx, sy) in zip(appearance.pupils, child_offsets):
        rx = iris_rx * params.pupil_ratio * spec.scale * spec.scale_x
        ry = iris_ry * params.pupil_ratio * spec.scale * spec.scale_y
        offset = ocular_local_to_world(
            (assembly_local[0] + sx, assembly_local[1] + sy), roll_deg=params.rotation_deg,
            alignment_axis_rotation_deg=params.alignment_axis_rotation_deg,
        )
        pupil_centers.append((center[0] + offset[0], center[1] + offset[1]))
        prx, pry, prot = project_ellipse_axes(
            rx, ry,
            alignment_axis_rotation_deg=params.alignment_axis_rotation_deg,
            roll_deg=params.rotation_deg,
        )
        pupil_radii.append((prx, pry))
        pupil_rotations.append(prot + spec.rotation_deg)
    reflection_local = (
        assembly_local[0] + params.reflection_x * iris_rx,
        assembly_local[1] + params.reflection_y * iris_ry,
    )
    reflection_offset = ocular_local_to_world(
        reflection_local, roll_deg=params.rotation_deg,
        alignment_axis_rotation_deg=params.alignment_axis_rotation_deg,
    )
    reflection_center = (center[0] + reflection_offset[0], center[1] + reflection_offset[1])
    reflection_rx, reflection_ry, reflection_rot = project_ellipse_axes(
        params.reflection_size * iris_rx, params.reflection_size * iris_ry,
        alignment_axis_rotation_deg=params.alignment_axis_rotation_deg,
        roll_deg=params.rotation_deg,
    )
    return (
        tuple(pupil_centers), tuple(pupil_radii), tuple(pupil_rotations),
        iris_center, (iris_rx_p, iris_ry_p), iris_rot, reflection_center,
        reflection_rx, reflection_ry, reflection_rot,
    )
