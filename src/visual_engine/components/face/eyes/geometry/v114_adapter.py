from __future__ import annotations

from .internal import resolve_pupil_child_offsets_local
from .v113_bridge import build_v113_spherical_layer
from .view_axis import OcularPose3D


def build_v114_spherical_layer(*, params, appearance, center, fw, assembly_local,
                               iris_rx, spherical_iris_rx, reference_width, reference_height,
                               upper_lid_points, lower_lid_points,
                               inner_canthus, outer_canthus, caruncle_points=(), epicanthic_fold_points=()):
    """Resolve the V1.14 globe plus lid coupling without bloating the legacy builder."""
    offsets = resolve_pupil_child_offsets_local(
        params, appearance, assembly_local=assembly_local, iris_rx=spherical_iris_rx, iris_ry=spherical_iris_rx,
        reference_width=reference_width, reference_height=reference_height,
    )
    # The globe is a parent volume behind the narrow facial aperture. Using the
    # full eye width as its radius made a 30° alignment rotation translate the
    # front optical pole by ~0.25 units, enough to eject the iris from a normal
    # eyelid opening. V1.18 derives a conservative globe radius from aperture
    # height and iris scale instead; this preserves a spherical parent without
    # making the visible iris jump out of the face at ordinary rotations.
    globe_radius = max(reference_height * 0.5, spherical_iris_rx * 1.20, 1e-9)
    return build_v113_spherical_layer(
        center=center, radius=globe_radius, params=params,
        pose=OcularPose3D(
            yaw_deg=params.ocular_yaw_deg, pitch_deg=params.ocular_pitch_deg,
            roll_deg=params.rotation_deg,
            alignment_axis_rotation_deg=params.alignment_axis_rotation_deg,
        ),
        iris_radius=spherical_iris_rx, pupil_radius=max(spherical_iris_rx * params.pupil_ratio, 1e-9),
        pupil_offsets_local=offsets,
        pupil_radii=tuple(spherical_iris_rx * params.pupil_ratio * spec.scale * spec.scale_x for spec in appearance.pupils),
        iris_offset_local=assembly_local, samples=max(64, params.contour_samples),
        upper_lid_points=upper_lid_points, lower_lid_points=lower_lid_points,
        inner_canthus=inner_canthus, outer_canthus=outer_canthus,
        caruncle_points=caruncle_points, epicanthic_fold_points=epicanthic_fold_points,
    )
