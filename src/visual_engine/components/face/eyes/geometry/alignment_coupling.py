from __future__ import annotations

from dataclasses import dataclass
import math

from .view_axis import OcularBasis3D, OcularPose3D, compose_ocular_basis


@dataclass(frozen=True, slots=True)
class AlignmentCouplingReport:
    """Explicit contract for alignment-axis rotation.

    The face-owned aperture is intentionally absent from the rotating globe. The
    globe, cornea, iris and pupil inherit the ocular basis; lid margins/canthi keep
    their face frame. This prevents the historical failure where alignment rotation
    was applied to the 2D eyelid contour and made the entire eye look like a tilted
    ellipse instead of a fixed aperture containing a rotated globe.
    """

    alignment_deg: float
    sign: str
    face_aperture_unchanged: bool
    globe_children_inherit: bool
    basis: OcularBasis3D


def alignment_sign(degrees: float) -> str:
    """Return the semantic sign used by prompt/debug tooling."""
    if not math.isfinite(degrees):
        raise ValueError("alignment rotation must be finite")
    if degrees > 0:
        return "alignment_positive"
    if degrees < 0:
        return "alignment_negative"
    return "alignment_neutral"


def resolve_alignment_coupling(
    *, parent_basis: OcularBasis3D | None = None,
    alignment_deg: float = 0.0,
) -> AlignmentCouplingReport:
    """Resolve the globe orientation without modifying the face-owned aperture.

    Positive rotation follows the right-hand rule around the local interocular X
    axis: anatomical +Y rotates toward +Z. Negative rotation is the inverse. The
    aperture/canthi/orbit remain in the parent face frame; only ocular children use
    the resulting basis.
    """
    pose = OcularPose3D(alignment_axis_rotation_deg=alignment_deg)
    basis = compose_ocular_basis(parent_basis, pose)
    return AlignmentCouplingReport(
        alignment_deg=alignment_deg,
        sign=alignment_sign(alignment_deg),
        face_aperture_unchanged=True,
        globe_children_inherit=True,
        basis=basis,
    )
