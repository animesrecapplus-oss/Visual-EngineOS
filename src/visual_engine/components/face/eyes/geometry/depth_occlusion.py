from __future__ import annotations

from dataclasses import dataclass
import math

from .orbital_surface import OrbitalSurface3D
from .spherical_assembly import Vec3

Point2 = tuple[float, float]


@dataclass(frozen=True, slots=True)
class DepthLayer:
    """Named depth layer for deterministic ocular painter/depth diagnostics."""
    name: str
    depth_min: float
    depth_max: float
    sample_count: int

    def __post_init__(self) -> None:
        if not all(math.isfinite(v) for v in (self.depth_min, self.depth_max)):
            raise ValueError("depth layer values must be finite")
        if self.depth_min > self.depth_max or self.sample_count < 0:
            raise ValueError("invalid depth layer")


@dataclass(frozen=True, slots=True)
class DepthVisibility:
    """Sampled depth result. ``visible_fraction`` is evidence, not anatomy."""
    visible_fraction: float
    hidden_fraction: float
    state: str
    depth_front_count: int
    depth_hidden_count: int


@dataclass(frozen=True, slots=True)
class OcularDepthOcclusion:
    """V1.15 depth contract between orbit, lids, globe and ocular children."""
    orbital_surface: OrbitalSurface3D
    upper_lid: DepthLayer
    lower_lid: DepthLayer
    iris: DepthLayer
    pupils: tuple[DepthLayer, ...]
    iris_visibility: DepthVisibility
    pupil_visibility: tuple[DepthVisibility, ...]
    aperture_states: tuple[str, ...]
    near_canthus: str
    far_canthus: str
    z_order: tuple[str, ...]


def _depth(p: Vec3, center: Vec3) -> float:
    # Camera convention inherited from projection3d.py: larger world Z is closer.
    return p[2] - center[2]


def _dist2(a: Point2, b: Point2) -> float:
    return (a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2


def _state(fraction: float) -> str:
    if fraction <= 0.0:
        return "hidden"
    if fraction >= 1.0:
        return "visible"
    return "partially_visible"


def _lid_depth_for_child(
    point: Point2,
    lid_points: tuple[Point2, ...],
    lid_points_3d: tuple[Vec3, ...],
    *,
    band: float,
) -> float | None:
    if not lid_points or len(lid_points) != len(lid_points_3d):
        return None
    limit2 = band * band
    best = None
    for p2, p3 in zip(lid_points, lid_points_3d):
        d2 = _dist2(point, p2)
        if d2 <= limit2 and (best is None or d2 < best[0]):
            best = (d2, p3[2])
    return None if best is None else best[1]


def _child_visibility(
    *,
    child_points: tuple[Point2, ...],
    child_points_3d: tuple[Vec3, ...],
    aperture_inside: tuple[bool, ...],
    upper_points: tuple[Point2, ...],
    upper_points_3d: tuple[Vec3, ...],
    lower_points: tuple[Point2, ...],
    lower_points_3d: tuple[Vec3, ...],
    center: Vec3,
    orbital_surface: OrbitalSurface3D,
    band: float,
) -> DepthVisibility:
    if not child_points:
        return DepthVisibility(0.0, 1.0, "hidden", 0, 0)
    visible = 0
    hidden = 0
    front = 0
    for point, point3, inside in zip(child_points, child_points_3d, aperture_inside):
        if not inside:
            hidden += 1
            continue
        lid_depths = []
        for pts2, pts3 in ((upper_points, upper_points_3d), (lower_points, lower_points_3d)):
            d = _lid_depth_for_child(point, pts2, pts3, band=band)
            if d is not None:
                lid_depths.append(d)
        child_depth = _depth(point3, center)
        orbital_depth = orbital_front = None
        # The orbital shell is used as the fallback depth surface where a lid
        # sample lies outside the spherical globe footprint. It is intentionally
        # not allowed to replace the globe: the globe remains the ocular parent.
        orbital_z = orbital_surface.front_z(point[0], -point[1])
        if orbital_z is not None:
            orbital_depth = orbital_z - center[2]
        occluder_depth = max(lid_depths) if lid_depths else orbital_depth
        # If the nearest foreground surface is closer to the camera than the
        # child, the child owns no pixel at that sample. The aperture remains the
        # global morphology boundary and this comparison is only a local depth gate.
        if occluder_depth is not None and occluder_depth >= child_depth - 1e-8:
            hidden += 1
        else:
            visible += 1
            front += int(occluder_depth is None or child_depth > occluder_depth)
    total = visible + hidden
    fraction = visible / total if total else 0.0
    return DepthVisibility(fraction, 1.0 - fraction, _state(fraction), front, hidden)


def resolve_ocular_depth(
    *,
    orbital_surface: OrbitalSurface3D,
    center: Vec3,
    upper_points: tuple[Point2, ...],
    upper_points_3d: tuple[Vec3, ...],
    lower_points: tuple[Point2, ...],
    lower_points_3d: tuple[Vec3, ...],
    iris_points: tuple[Point2, ...],
    iris_points_3d: tuple[Vec3, ...],
    pupil_points: tuple[tuple[Point2, ...], ...],
    pupil_points_3d: tuple[tuple[Vec3, ...], ...],
    aperture_inside_iris: tuple[bool, ...],
    aperture_inside_pupils: tuple[tuple[bool, ...], ...],
    near_canthus: str,
    far_canthus: str,
    band: float,
) -> OcularDepthOcclusion:
    """Resolve local depth occlusion without replacing the renderer's aperture clip."""
    if band <= 0 or not math.isfinite(band):
        raise ValueError("depth occlusion band must be finite and > 0")
    def layer(name: str, points: tuple[Vec3, ...]) -> DepthLayer:
        depths = [_depth(p, center) for p in points]
        return DepthLayer(name, min(depths, default=0.0), max(depths, default=0.0), len(depths))

    iris_visibility = _child_visibility(
        child_points=iris_points, child_points_3d=iris_points_3d,
        aperture_inside=aperture_inside_iris, upper_points=upper_points,
        upper_points_3d=upper_points_3d, lower_points=lower_points,
        lower_points_3d=lower_points_3d, center=center, orbital_surface=orbital_surface, band=band,
    )
    pupil_visibility = tuple(_child_visibility(
        child_points=p2, child_points_3d=p3, aperture_inside=inside,
        upper_points=upper_points, upper_points_3d=upper_points_3d,
        lower_points=lower_points, lower_points_3d=lower_points_3d,
        center=center, orbital_surface=orbital_surface, band=band,
    ) for p2, p3, inside in zip(pupil_points, pupil_points_3d, aperture_inside_pupils))
    return OcularDepthOcclusion(
        orbital_surface=orbital_surface,
        upper_lid=layer("upper_lid", upper_points_3d),
        lower_lid=layer("lower_lid", lower_points_3d),
        iris=layer("iris", iris_points_3d),
        pupils=tuple(layer(f"pupil_{i}", p) for i, p in enumerate(pupil_points_3d)),
        iris_visibility=iris_visibility,
        pupil_visibility=pupil_visibility,
        aperture_states=(iris_visibility.state,) + tuple(v.state for v in pupil_visibility),
        near_canthus=near_canthus,
        far_canthus=far_canthus,
        z_order=("orbit", "sclera", "iris", "pupil", "cornea", "eyelid"),
    )
