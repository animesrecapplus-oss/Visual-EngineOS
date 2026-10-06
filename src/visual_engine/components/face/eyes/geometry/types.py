from dataclasses import dataclass
from typing import Literal

from ..contracts.types import EyeShape, EyeState
from ..gaze.solver import GazeSolution

@dataclass(frozen=True, slots=True)
class Coverage:
    covered: bool = False
    fraction: float = 0.0
    mode: Literal["opaque", "transparent"] = "opaque"

    def __post_init__(self) -> None:
        if not 0 <= self.fraction <= 1:
            raise ValueError("coverage fraction must be within [0,1]")
        if self.mode not in {"opaque", "transparent"}:
            raise ValueError("unknown coverage mode")
        if self.covered and self.fraction == 0:
            object.__setattr__(self, "fraction", 1.0)


@dataclass(frozen=True, slots=True)
class EyeGeometry:
    center_x: float
    center_y: float
    outer_path: tuple[tuple[float, float], ...]
    # Cubic canthus bridges close the aperture with explicit C1 tangent contracts.
    outer_canthus_bridge: tuple[tuple[float, float], ...]
    inner_canthus_bridge: tuple[tuple[float, float], ...]
    upper_lid_points: tuple[tuple[float, float], ...]
    lower_lid_points: tuple[tuple[float, float], ...]
    upper_crease_points: tuple[tuple[float, float], ...]
    lower_crease_points: tuple[tuple[float, float], ...]
    inner_canthus: tuple[float, float]
    outer_canthus: tuple[float, float]
    # Separate medial skin-fold curve; morphology-owned and renderer-optional.
    epicanthic_fold_points: tuple[tuple[float, float], ...]
    medial_caruncle_points: tuple[tuple[float, float], ...]
    contour_points: tuple[tuple[float, float], ...]
    iris_center: tuple[float, float]
    iris_rx: float
    iris_ry: float
    iris_rotation_deg: float
    pupil_centers: tuple[tuple[float, float], ...]
    pupil_radii: tuple[tuple[float, float], ...]
    pupil_rotation_degs: tuple[float, ...]
    reflection_center: tuple[float, float]
    reflection_rx: float
    reflection_ry: float
    reflection_rotation_deg: float
    reflection_radius: float
    opening: float
    rotation_deg: float
    alignment_axis_rotation_deg: float
    side: Literal["single", "image_left", "image_right"]
    gaze_solution: GazeSolution
    state: EyeState
    shape: EyeShape
    # Stable superior reference frame used by features (notably eyebrows) that
    # must not collapse when the visible aperture closes.
    brow_reference_top_y: float
    brow_reference_top_local_y: float
    brow_reference_scale: float
    # V1.13 is optional metadata so all historical EyeGeometry constructors remain valid.
    ocular_yaw_deg: float = 0.0
    ocular_pitch_deg: float = 0.0
    spherical_assembly: object | None = None

    @property
    def nominal_width(self) -> float:
        return max(x for x, _ in self.contour_points) - min(x for x, _ in self.contour_points)

    @property
    def visible_height(self) -> float:
        return max(y for _, y in self.contour_points) - min(y for _, y in self.contour_points)

    @property
    def pupil_rx(self) -> float:
        return self.pupil_radii[0][0]

    @property
    def pupil_ry(self) -> float:
        return self.pupil_radii[0][1]

    @property
    def pupil_center(self) -> tuple[float, float]:
        return self.pupil_centers[0]
