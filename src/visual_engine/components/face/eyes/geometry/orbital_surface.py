from __future__ import annotations

from dataclasses import dataclass
import math

from .spherical_assembly import Vec3
from .projection3d import Camera3D, Point2, project_point


@dataclass(frozen=True, slots=True)
class OrbitalSurface3D:
    """Face/orbital shell used as a depth surface around the ocular aperture.

    The shell is deliberately an ellipsoid rather than a second eyeball. It is a
    geometric approximation of the local orbital/soft-tissue surface, not an
    anatomical claim. Its sole V1.15 authority is depth ordering around the lid.
    """

    center: Vec3
    radius_x: float
    radius_y: float
    radius_z: float
    front_offset: float = 0.0

    def __post_init__(self) -> None:
        values = self.center + (self.radius_x, self.radius_y, self.radius_z, self.front_offset)
        if not all(math.isfinite(v) for v in values):
            raise ValueError("orbital surface values must be finite")
        if min(self.radius_x, self.radius_y, self.radius_z) <= 0:
            raise ValueError("orbital surface radii must be > 0")

    def front_z(self, x: float, y: float) -> float | None:
        """Return the camera-facing ellipsoid intersection at screen x/y."""
        cx, cy, cz = self.center
        nx = (x - cx) / self.radius_x
        ny = (y - cy) / self.radius_y
        rem = 1.0 - nx * nx - ny * ny
        if rem < -1e-12:
            return None
        return cz + self.front_offset + self.radius_z * math.sqrt(max(0.0, rem))

    def project_outline(self, camera: Camera3D, samples: int = 96) -> tuple[Point2, ...]:
        """Project the front silhouette of the shell for diagnostics only."""
        if samples < 32:
            raise ValueError("orbital surface outline requires at least 32 samples")
        cx, cy, cz = self.center
        return tuple(project_point((cx + self.radius_x * math.cos(t),
                                    cy + self.radius_y * math.sin(t),
                                    cz + self.front_offset), camera)
                     for t in (2.0 * math.pi * i / samples for i in range(samples)))


def build_orbital_surface(center: Vec3, globe_radius: float) -> OrbitalSurface3D:
    """Construct a conservative local orbital shell from the globe scale.

    The shell is wider and shallower than the globe. It sits slightly in front of
    the globe at the lid boundary; this permits a depth comparison without making
    the shell a fake anatomical replacement for the face.
    """
    if globe_radius <= 0 or not math.isfinite(globe_radius):
        raise ValueError("globe_radius must be finite and > 0")
    return OrbitalSurface3D(
        center=center,
        radius_x=globe_radius * 1.18,
        radius_y=globe_radius * 0.82,
        radius_z=globe_radius * 0.30,
        front_offset=globe_radius * 0.025,
    )
