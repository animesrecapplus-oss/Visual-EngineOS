"""Renderer-neutral ocular geometry result types."""
from .types import Coverage, EyeGeometry
from .orientation import project_alignment_axis, ocular_local_to_world, face_local_to_world, project_ellipse_axes
from .internal import build_projected_internal_assembly
from .view_axis import OcularBasis3D, OcularPose3D, basis_handedness, compose_ocular_basis, rotate_vector
from .projection3d import Camera3D, project_oriented_circle, project_point, project_sphere_silhouette
from .spherical_assembly import SphericalEyeAssembly, SurfaceVisibility, build_spherical_eye_assembly
from .eyelid_surface import EyelidSurfaceCoupling, SurfaceTrace3D, couple_eyelids_to_globe
from .occlusion import ApertureOcclusion, measure_aperture_occlusion

from .orbital_surface import OrbitalSurface3D, build_orbital_surface
from .depth_occlusion import DepthLayer, DepthVisibility, OcularDepthOcclusion, resolve_ocular_depth

from .alignment_coupling import AlignmentCouplingReport, alignment_sign, resolve_alignment_coupling
