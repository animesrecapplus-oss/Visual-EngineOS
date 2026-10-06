from __future__ import annotations

from dataclasses import replace

from .eyelid_surface import couple_eyelids_to_globe
from .orbital_surface import build_orbital_surface
from .depth_occlusion import resolve_ocular_depth
from .occlusion import _inside, measure_aperture_occlusion
from .projection3d import Camera3D
from .spherical_assembly import SphericalEyeAssembly, build_spherical_eye_assembly
from .view_axis import OcularPose3D
from .alignment_surface_coupling import couple_lid_curve


def build_v113_spherical_layer(
    *, center, radius, pose, iris_radius, pupil_radius, samples, params,
    iris_offset_local=(0.0, 0.0), pupil_offsets_local=(), pupil_radii=(),
    upper_lid_points=(), lower_lid_points=(), inner_canthus=(0.0, 0.0),
    outer_canthus=(0.0, 0.0), caruncle_points=(), epicanthic_fold_points=(), self_intersections_2d=0,
):
    """Build the spherical parent and its V1.14 lid/depth coupling in one adapter."""
    assembly = build_spherical_eye_assembly(
        center=(center[0], -center[1], 0.0), radius=radius, pose=pose,
        iris_radius=iris_radius, pupil_radius=pupil_radius,
        pupil_offsets_local=pupil_offsets_local, pupil_radii=pupil_radii,
        camera=Camera3D(orthographic=True), samples=samples,
        iris_offset_local=(iris_offset_local[0], -iris_offset_local[1]),
    )
    # ``project_point`` already returns the historical SVG +Y-down screen frame.
    # V1.18 removes the old second Y inversion that had been introduced here under
    # the mistaken assumption that the projection was still +Y-up. That double
    # inversion was invisible at alignment=0 but mirrored every non-zero alignment
    # vertically, causing the iris to leave the aperture and making the eye look
    # like a detached pupil.
    def _screen_point(point):
        return point

    assembly = replace(
        assembly,
        sclera_silhouette=tuple(_screen_point(p) for p in assembly.sclera_silhouette),
        cornea_outline=tuple(_screen_point(p) for p in assembly.cornea_outline),
        iris_outline=tuple(_screen_point(p) for p in assembly.iris_outline),
        pupil_outline=tuple(_screen_point(p) for p in assembly.pupil_outline),
        pupil_outlines=tuple(tuple(_screen_point(p) for p in outline) for outline in assembly.pupil_outlines),
        iris_projected_center=_screen_point(assembly.iris_projected_center) if assembly.iris_projected_center else None,
        pupil_projected_centers=tuple(_screen_point(p) for p in assembly.pupil_projected_centers),
    )

    projected_upper, upper_surface_points = couple_lid_curve(
        tuple(upper_lid_points), center=assembly.center, radius=assembly.radius, basis=assembly.basis,
        follow_strength=params.eyelid_surface_follow_strength,
    )
    projected_lower, lower_surface_points = couple_lid_curve(
        tuple(lower_lid_points), center=assembly.center, radius=assembly.radius, basis=assembly.basis,
        follow_strength=params.eyelid_surface_follow_strength,
    )
    coupling = couple_eyelids_to_globe(
        upper=projected_upper, lower=projected_lower,
        inner_canthus=(inner_canthus[0], -inner_canthus[1]),
        outer_canthus=(outer_canthus[0], -outer_canthus[1]),
        center=assembly.center, radius=assembly.radius, basis=assembly.basis,
        caruncle=tuple((x, -y) for x, y in caruncle_points),
        epicanthus=tuple((x, -y) for x, y in epicanthic_fold_points),
        self_intersections_2d=self_intersections_2d,
    )
    aperture = tuple(projected_upper) + tuple(reversed(projected_lower))
    occlusion = measure_aperture_occlusion(
        aperture=aperture, iris=assembly.iris_outline, pupils=assembly.pupil_outlines,
    )
    visibility = replace(
        assembly.visibility, iris=occlusion.iris_state,
        pupil=(occlusion.pupil_states[0] if occlusion.pupil_states else "hidden"),
    )
    aperture_flags_iris = tuple(_inside(point, aperture) for point in assembly.iris_outline)
    aperture_flags_pupils = tuple(tuple(_inside(point, aperture) for point in outline) for outline in assembly.pupil_outlines)
    orbital = build_orbital_surface(assembly.center, assembly.radius)
    depth = resolve_ocular_depth(
        orbital_surface=orbital, center=assembly.center,
        upper_points=tuple(projected_upper), upper_points_3d=upper_surface_points,
        lower_points=tuple(projected_lower), lower_points_3d=lower_surface_points,
        iris_points=assembly.iris_outline, iris_points_3d=assembly.iris_surface_samples,
        pupil_points=assembly.pupil_outlines, pupil_points_3d=assembly.pupil_surface_samples,
        aperture_inside_iris=aperture_flags_iris, aperture_inside_pupils=aperture_flags_pupils,
        near_canthus=coupling.near_canthus, far_canthus=coupling.far_canthus,
        band=max(assembly.radius * 0.08, 1e-6),
    )
    return replace(
        assembly, visibility=visibility, eyelid_coupling=replace(coupling, projected_upper=projected_upper, projected_lower=projected_lower),
        iris_aperture_fraction=occlusion.iris_fraction,
        pupil_aperture_fractions=occlusion.pupil_fractions, depth_occlusion=depth,
    )


def apply_v113_projected_internal_values(
    *, assembly: SphericalEyeAssembly, iris_center_world,
    iris_rx, iris_ry, pupil_centers, pupil_radii, pupil_rotation_degs,
    pupil_count,
):
    """Adapt projected spherical children to the legacy EyeGeometry fields."""
    if assembly.visibility.iris != "hidden" and assembly.iris_outline:
        pts = assembly.iris_outline
        iris_center_world = assembly.iris_projected_center or iris_center_world
        min_x, max_x = min(x for x, _ in pts), max(x for x, _ in pts)
        min_y, max_y = min(y for _, y in pts), max(y for _, y in pts)
        iris_rx = max((max_x - min_x) * .5, 1e-12)
        iris_ry = max((max_y - min_y) * .5, 1e-12)
    if assembly.visibility.pupil == "hidden" or not assembly.pupil_outlines:
        # Keep the historical EyeGeometry children available for compatibility;
        # renderer visibility is governed by the spherical assembly state.
        return iris_center_world, iris_rx, iris_ry, tuple(pupil_centers[:pupil_count]), tuple(pupil_radii[:pupil_count]), tuple(pupil_rotation_degs[:pupil_count])
    centers, radii = [], []
    for pts in assembly.pupil_outlines[:pupil_count]:
        min_x, max_x = min(x for x, _ in pts), max(x for x, _ in pts)
        min_y, max_y = min(y for _, y in pts), max(y for _, y in pts)
        centers.append(assembly.pupil_projected_centers[len(centers)] if len(assembly.pupil_projected_centers) > len(centers) else ((min_x + max_x) * .5, (min_y + max_y) * .5))
        radii.append(((max_x - min_x) * .5, (max_y - min_y) * .5))
    # Keep the historical EyeGeometry rotation field as an API compatibility
    # channel. The actual spherical child orientation is stored in
    # ``assembly.pupil_projection_rotations`` and rendered from its sampled path.
    return iris_center_world, iris_rx, iris_ry, tuple(centers), tuple(radii), tuple(pupil_rotation_degs[:len(centers)])
