from __future__ import annotations
import math
from ..contracts.types import EyeState
from ..morphology.spec import EyeParameters
from ..appearance.spec import EyeAppearance
from ..gaze.solver import Gaze, GazeSolver, BinocularGazeSolver, BinocularGazeSolution
from .types import EyeGeometry
from .shape import _shape_factors
from .contour import _contour, _bounds
from .curve import _sample_subcurve, _offset_curve
from .lid_follow import _apply_gaze_lid_follow
from .invariants import assert_finite_contour, has_self_intersection
from .continuity import build_canthus_bridges, assess_contour_continuity, closed_contour_samples
from .epicanthic import build_epicanthic_fold
from .caruncle import build_medial_caruncle
from .transform import world_relative_to_local, gaze_to_local
from .orientation import face_local_to_world
from .internal import build_projected_internal_assembly
from .v113_bridge import apply_v113_projected_internal_values
from .v114_adapter import build_v114_spherical_layer
from .alignment_surface_coupling import rebuild_coupled_aperture
def _world(center: tuple[float, float], point: tuple[float, float], p: EyeParameters) -> tuple[float, float]:
    # The eyelid aperture is face-owned. Alignment-axis rotation belongs to the
    # ocular globe only, so it must never foreshorten the lid margins/canthi.
    x, y = face_local_to_world(point, roll_deg=p.rotation_deg)
    return center[0] + x, center[1] + y
def build_eye_geometry(
    params: EyeParameters | None = None,
    *,
    center: tuple[float, float] = (0.0, 0.0),
    state: EyeState = "normal",
    gaze: Gaze | None = None,
    appearance: EyeAppearance | None = None,
    expression: str = "neutral",
    side: str = "single",
) -> EyeGeometry:
    p = params or EyeParameters()
    if side not in {"single", "image_left", "image_right"}:
        raise ValueError("side must be single, image_left, or image_right")
    mirror_x = side == "image_left"
    a = appearance or EyeAppearance()
    if expression != "neutral":
        from ..expression import OcularExpressionSolver
        resolved = OcularExpressionSolver.solve(p, a, expression)
        p, a = resolved.parameters, resolved.appearance
    g = gaze or Gaze()
    if state not in {"normal", "irritated", "covered", "damaged", "closed", "wide_open", "crying"}:
        raise ValueError("unknown eye state")
    opening = 0.0 if state in {"closed", "covered"} else (1.0 if state == "wide_open" else p.opening)
    fw, fh = _shape_factors(p.shape)
    half_w = p.width * 0.5 * fw
    half_h = p.height * 0.5 * fh * max(opening, 1e-6)
    # `_contour` returns geometry already rotated around the eye origin. Keep a
    # canonical local copy for gaze/lid-follow; only the final geometry crosses
    # the parent-rotation boundary. This prevents a 90° parent rotation from
    # making the solver interpret world-up as eye-local-up.
    contour_world_rel = _contour(p, half_w, half_h, opening, mirror_x=mirror_x)
    angle = math.radians(p.rotation_deg)
    ca, sa = math.cos(angle), math.sin(angle)
    contour = tuple(world_relative_to_local(point, p.rotation_deg) for point in contour_world_rel)
    assert_finite_contour(contour)
    if opening > 0.0 and has_self_intersection(contour):
        raise ValueError("eye contour self-intersection detected")
    reference_half_h = p.height * 0.5 * fh
    reference_contour = _contour(p, half_w, reference_half_h, 1.0, mirror_x=mirror_x)
    reference_upper_world = reference_contour[:len(reference_contour)//2]
    reference_upper_local = tuple(world_relative_to_local(point, p.rotation_deg) for point in reference_upper_world)
    reference_crease_local = _offset_curve(
        _sample_subcurve(reference_upper_local, a.eyelid.upper_crease_length),
        a.eyelid.upper_crease_offset * max(reference_half_h, 1e-9), -1.0
    )
    top_point_local = min(reference_crease_local, key=lambda point: point[1])
    brow_reference_top_local_y = top_point_local[1]
    top_world_y = center[1] + sa * top_point_local[0] + ca * top_point_local[1]
    brow_reference_top_y = top_world_y
    brow_reference_scale = max(
        max(y for _, y in reference_upper_local) - min(y for _, y in reference_upper_local),
        p.width * fw * 0.05,
        1e-9,
    )
    if opening == 0.0:
        # A closed eye is still an oriented eyelid gesture. Flatten only in the
        # canonical local frame; flattening after rotation was the exact cause of
        # the V1.8 artifact where lashes/brow rotated but the closed lid stayed
        # horizontal.
        contour = tuple((x, 0.0) for x, _ in contour)
    translated = tuple(_world(center, point, p) for point in contour)
    upper_local = contour[:len(contour)//2]
    lower_local = tuple(reversed(contour[len(contour)//2:]))
    upper_lid_points = tuple(_world(center, point, p) for point in upper_local)
    lower_lid_points = tuple(_world(center, point, p) for point in lower_local)
    inner_canthus = upper_lid_points[0]
    outer_canthus = upper_lid_points[-1]
    outer_path = translated
    upper_crease_local = _offset_curve(
        _sample_subcurve(upper_local, a.eyelid.upper_crease_length),
        a.eyelid.upper_crease_offset * max(half_h, 1e-9), -1.0
    )
    lower_crease_local = _offset_curve(
        _sample_subcurve(lower_local, a.eyelid.lower_crease_length),
        a.eyelid.lower_crease_offset * max(half_h, 1e-9), 1.0
    )
    upper_crease_points = tuple(_world(center, point, p) for point in upper_crease_local)
    lower_crease_points = tuple(_world(center, point, p) for point in reversed(lower_crease_local))
    min_x, max_x, min_y, max_y = _bounds(contour)
    # Internal ocular offsets use the nominal morphology frame, not the sampled
    # contour bounds. Otherwise contour irregularity/wave would accidentally move
    # the iris and pupil: a direct violation of MOR.morph_orthogonality.
    reference_width = p.width * fw
    reference_height = p.height * fh * opening
    ix = p.iris_offset_x * reference_width * 0.5
    iy = p.iris_offset_y * reference_height * 0.5
    # The iris/pupil are one rigid ocular assembly. The pupil is the aperture in
    # the iris; it does not independently orbit inside a fixed iris during gaze.
    # This distinction fixes the earlier visual error where internal parts could
    # appear to slide independently.
    nominal_half_h = p.height * fh * opening * 0.5
    iris_rx = max(1e-9, nominal_half_h * p.iris_ratio)
    iris_ry = iris_rx
    # First resolve direction against the undeformed aperture. We then apply the
    # small lid-follow deformation and resolve containment again against the final
    # aperture. This is a two-pass solve, not a hidden renderer-side correction.
    local_gaze = gaze_to_local(g, center, p.rotation_deg)
    provisional = GazeSolver.solve(
        local_gaze, contour, center=(0.0, 0.0), iris_center=(ix, iy), iris_rx=iris_rx, iris_ry=iris_ry,
        pupil_rx=iris_rx * p.pupil_ratio, pupil_ry=iris_ry * p.pupil_ratio,
    )
    upper_local, lower_local = _apply_gaze_lid_follow(
        upper_local, lower_local, provisional.normalized_x, provisional.normalized_y,
        max(half_h, 1e-9), g.strength * g.amplitude, 0.0,
    )
    upper_lid_points = tuple(_world(center, point, p) for point in upper_local)
    lower_lid_points = tuple(_world(center, point, p) for point in lower_local)
    contour = tuple(upper_lid_points + tuple(reversed(lower_lid_points)))
    assert_finite_contour(contour)
    if opening > 0.0 and has_self_intersection(contour):
        raise ValueError("eye contour self-intersection detected after gaze deformation")
    outer_path = contour
    if opening > 0.0:
        outer_bridge = (
            build_canthus_bridges(upper_lid_points, lower_lid_points)[0]
            if p.canthus_outer_terminal.mode == "bridge" else ()
        )
        inner_bridge = (
            build_canthus_bridges(upper_lid_points, lower_lid_points)[1]
            if p.canthus_inner_terminal.mode == "bridge" else ()
        )
        continuity = assess_contour_continuity(
            upper_lid_points, lower_lid_points, outer_bridge, inner_bridge
        )
        if not continuity.valid:
            raise ValueError(f"eye contour continuity invariant failed: max_error={continuity.max_error:.3e}")
        closed_samples = closed_contour_samples(
            upper_lid_points, lower_lid_points, outer_bridge, inner_bridge
        )
        assert_finite_contour(closed_samples)
        if has_self_intersection(closed_samples):
            raise ValueError("eye contour self-intersection detected across canthus terminals")
    else:
        # A closed/covered eye intentionally collapses its visible aperture; no
        # non-degenerate canthus bridge is claimed for this representation.
        outer_bridge = ()
        inner_bridge = ()
    inner_canthus = upper_lid_points[0]
    outer_canthus = upper_lid_points[-1]
    caruncle_points = build_medial_caruncle(
        inner_canthus, center,
        width=a.caruncle.width * p.width * fw,
        height=a.caruncle.height * p.height * fh,
        curvature=a.caruncle.curvature,
    ) if opening > 0 and a.caruncle.enabled else ()
    epicanthic_fold_points = build_epicanthic_fold(
        upper_lid_points[0], lower_lid_points[0], p.epicanthic_fold, min(half_w, half_h), interior_target=center
    )
    upper_crease_local = _offset_curve(
        _sample_subcurve(upper_local, a.eyelid.upper_crease_length),
        a.eyelid.upper_crease_offset * max(half_h, 1e-9), -1.0
    )
    lower_crease_local = _offset_curve(
        _sample_subcurve(lower_local, a.eyelid.lower_crease_length),
        a.eyelid.lower_crease_offset * max(half_h, 1e-9), 1.0
    )
    upper_crease_points = tuple(_world(center, point, p) for point in upper_crease_local)
    lower_crease_points = tuple(_world(center, point, p) for point in reversed(lower_crease_local))
    final_local_contour = tuple(upper_local + tuple(reversed(lower_local)))
    final_gaze = GazeSolver.solve(
        local_gaze, final_local_contour, center=(0.0, 0.0),
        iris_center=(ix, iy), iris_rx=iris_rx, iris_ry=iris_ry,
        pupil_rx=iris_rx * p.pupil_ratio, pupil_ry=iris_ry * p.pupil_ratio,
    )
    assembly_x = ix + final_gaze.offset_x
    assembly_y = iy + final_gaze.offset_y
    (pupil_centers, pupil_radii, pupil_rotation_degs, iris_center_world,
     (projected_iris_rx, projected_iris_ry), projected_iris_rotation, reflection_center,
     projected_reflection_rx, projected_reflection_ry, projected_reflection_rotation) = build_projected_internal_assembly(
        p, a, center=center, assembly_local=(assembly_x, assembly_y), iris_rx=iris_rx, iris_ry=iris_ry,
        reference_width=reference_width, reference_height=reference_height
    )
    gaze_solution = final_gaze
    spherical_assembly = None
    if any(abs(v) > 1e-12 for v in (p.ocular_yaw_deg, p.ocular_pitch_deg, p.alignment_axis_rotation_deg)):
        spherical_assembly = build_v114_spherical_layer(
            params=p, appearance=a, center=center, fw=fw,
            assembly_local=(assembly_x, assembly_y), iris_rx=iris_rx,
            spherical_iris_rx=max(iris_rx, reference_half_h * p.iris_ratio),
            reference_width=reference_width, reference_height=reference_height,
            upper_lid_points=upper_lid_points, lower_lid_points=lower_lid_points,
            inner_canthus=inner_canthus, outer_canthus=outer_canthus,
            caruncle_points=caruncle_points, epicanthic_fold_points=epicanthic_fold_points,
        )
        (iris_center_world, projected_iris_rx, projected_iris_ry, pupil_centers,
         pupil_radii, pupil_rotation_degs) = apply_v113_projected_internal_values(
            assembly=spherical_assembly, iris_center_world=iris_center_world,
            iris_rx=projected_iris_rx, iris_ry=projected_iris_ry,
            pupil_centers=pupil_centers, pupil_radii=pupil_radii,
            pupil_rotation_degs=pupil_rotation_degs, pupil_count=len(a.pupils),
        )
        coupling = spherical_assembly.eyelid_coupling
        if coupling is not None and getattr(coupling, "projected_upper", ()):
            upper_lid_points, lower_lid_points, contour, outer_bridge, inner_bridge = rebuild_coupled_aperture(
                tuple(coupling.projected_upper), tuple(coupling.projected_lower),
                outer_bridge_mode=p.canthus_outer_terminal.mode,
                inner_bridge_mode=p.canthus_inner_terminal.mode,
            )
            outer_path = contour
    return EyeGeometry(
        center_x=center[0], center_y=center[1], outer_path=outer_path,
        outer_canthus_bridge=outer_bridge, inner_canthus_bridge=inner_bridge,
        upper_lid_points=upper_lid_points, lower_lid_points=lower_lid_points,
        upper_crease_points=upper_crease_points, lower_crease_points=lower_crease_points,
        inner_canthus=inner_canthus, outer_canthus=outer_canthus, epicanthic_fold_points=epicanthic_fold_points, medial_caruncle_points=caruncle_points, contour_points=contour,
        iris_center=iris_center_world, iris_rx=projected_iris_rx, iris_ry=projected_iris_ry, iris_rotation_deg=projected_iris_rotation,
        pupil_centers=tuple(pupil_centers), pupil_radii=tuple(pupil_radii), pupil_rotation_degs=tuple(pupil_rotation_degs),
        reflection_center=reflection_center, reflection_rx=projected_reflection_rx, reflection_ry=projected_reflection_ry,
        reflection_rotation_deg=projected_reflection_rotation, reflection_radius=min(projected_reflection_rx, projected_reflection_ry),
        opening=opening, rotation_deg=p.rotation_deg, alignment_axis_rotation_deg=p.alignment_axis_rotation_deg, side=side, gaze_solution=gaze_solution,
        state=state, shape=p.shape, brow_reference_top_y=brow_reference_top_y,
        brow_reference_top_local_y=brow_reference_top_local_y,
        brow_reference_scale=brow_reference_scale,
        ocular_yaw_deg=p.ocular_yaw_deg, ocular_pitch_deg=p.ocular_pitch_deg,
        spherical_assembly=spherical_assembly,
    )
