from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Iterable

from .digitization import Point, ReferenceSample
from ..geometry.types import EyeGeometry


@dataclass(frozen=True, slots=True)
class ReferenceEngineAlignment:
    """Fixed diagnostic mapping; it never fits engine geometry to the reference."""
    reference_medial_px: Point
    reference_lateral_px: Point
    engine_medial: Point
    engine_lateral: Point
    reference_normal_scale: float
    engine_normal_scale: float

    def __post_init__(self) -> None:
        if self.reference_normal_scale <= 0 or self.engine_normal_scale <= 0:
            raise ValueError("overlay normal scales must be positive")

    def map(self, point: Point) -> Point:
        return _map(point, self.reference_medial_px, self.reference_lateral_px, self.engine_medial, self.engine_lateral,
                    self.reference_normal_scale, self.engine_normal_scale)

    def inverse_map(self, point: Point) -> Point:
        return _map(point, self.engine_medial, self.engine_lateral, self.reference_medial_px, self.reference_lateral_px,
                    self.engine_normal_scale, self.reference_normal_scale)


def _map(point: Point, src0: Point, src1: Point, dst0: Point, dst1: Point, src_normal: float, dst_normal: float) -> Point:
    sx, sy = src1[0] - src0[0], src1[1] - src0[1]
    dx, dy = dst1[0] - dst0[0], dst1[1] - dst0[1]
    sl, dl = math.hypot(sx, sy), math.hypot(dx, dy)
    if min(sl, dl) <= 1e-12:
        raise ValueError("overlay terminal axis is degenerate")
    su, sv = sx / sl, sy / sl
    du, dv = dx / dl, dy / dl
    snx, sny, dnx, dny = -sv, su, -dv, du
    px, py = point[0] - src0[0], point[1] - src0[1]
    along, normal = px * su + py * sv, px * snx + py * sny
    return (dst0[0] + du * along * dl / sl + dnx * normal * dst_normal / src_normal,
            dst0[1] + dv * along * dl / sl + dny * normal * dst_normal / src_normal)


def _resample(points: tuple[Point, ...], count: int) -> tuple[Point, ...]:
    if len(points) < 2 or count < 2:
        raise ValueError("polyline resampling requires two points")
    lengths = [math.dist(a, b) for a, b in zip(points, points[1:])]
    total = sum(lengths)
    if total <= 1e-12:
        raise ValueError("cannot resample a zero-length polyline")
    out = [points[0]]; seg = 0; walked = 0.0
    for target in (total * i / (count - 1) for i in range(1, count - 1)):
        while seg < len(lengths) - 1 and walked + lengths[seg] < target:
            walked += lengths[seg]; seg += 1
        f = (target - walked) / max(lengths[seg], 1e-12)
        a, b = points[seg], points[seg + 1]
        out.append((a[0] + f * (b[0] - a[0]), a[1] + f * (b[1] - a[1])))
    out.append(points[-1])
    return tuple(out)


def polyline_error(reference_points: Iterable[Point], engine_points: Iterable[Point], alignment: ReferenceEngineAlignment) -> dict[str, float]:
    engine = tuple(engine_points)
    if len(engine) < 2:
        raise ValueError("engine polyline requires two points")
    reference = _resample(tuple(alignment.map(p) for p in reference_points), len(engine))
    distances = [math.dist(a, b) for a, b in zip(reference, engine)]
    return {"mean_error": sum(distances) / len(distances), "max_error": max(distances),
            "rms_error": math.sqrt(sum(d * d for d in distances) / len(distances))}


def _tangent_error(ref: ReferenceSample, engine: EyeGeometry, alignment: ReferenceEngineAlignment, *, endpoint: str, upper: bool) -> float:
    curve = ref.upper if upper else ref.lower
    if curve is None:
        raise ValueError("reference curve missing")
    rt = curve.tangent_start if endpoint == "start" else curve.tangent_end
    et_curve = engine.upper_lid_points if upper else engine.lower_lid_points
    if endpoint == "start":
        et = (et_curve[1][0] - et_curve[0][0], et_curve[1][1] - et_curve[0][1])
        base = curve.points_px[0]
    else:
        et = (et_curve[-1][0] - et_curve[-2][0], et_curve[-1][1] - et_curve[-2][1])
        base = curve.points_px[-1]
    # Map the tangent from the same endpoint.  The previous implementation used
    # the first reference point even for the outer endpoint, which could report a
    # plausible-looking but geometrically unrelated tangent error.
    mapped_tip = alignment.map((base[0] + rt[0], base[1] + rt[1]))
    mapped_base = alignment.map(base)
    rtm = (mapped_tip[0] - mapped_base[0], mapped_tip[1] - mapped_base[1])
    ra, ea = math.atan2(rtm[1], rtm[0]), math.atan2(et[1], et[0])
    return abs((math.degrees(ra - ea) + 180.0) % 360.0 - 180.0)


def overlay_metrics(sample: ReferenceSample, engine: EyeGeometry, alignment: ReferenceEngineAlignment) -> dict[str, object]:
    """Compare approved pixel fields against engine geometry without fitting."""
    result: dict[str, object] = {"sample_id": sample.sample_id, "family": sample.family.value}
    if sample.upper:
        result["upper_error"] = polyline_error(sample.upper.points_px, engine.upper_lid_points, alignment)
        result["inner_upper_tangent_error_deg"] = _tangent_error(sample, engine, alignment, endpoint="start", upper=True)
        result["outer_upper_tangent_error_deg"] = _tangent_error(sample, engine, alignment, endpoint="end", upper=True)
    if sample.lower:
        result["lower_error"] = polyline_error(sample.lower.points_px, engine.lower_lid_points, alignment)
        result["inner_lower_tangent_error_deg"] = _tangent_error(sample, engine, alignment, endpoint="start", upper=False)
        result["outer_lower_tangent_error_deg"] = _tangent_error(sample, engine, alignment, endpoint="end", upper=False)
    if sample.medial_terminal_px:
        mapped = alignment.map(sample.medial_terminal_px)
        result["medial_terminal_error"] = math.dist(mapped, engine.inner_canthus)
    if sample.lateral_terminal_px:
        mapped = alignment.map(sample.lateral_terminal_px)
        result["lateral_terminal_error"] = math.dist(mapped, engine.outer_canthus)
    # Caruncle/epicanthus are deliberately omitted when not explicitly digitized.
    return result


def render_reference_engine_overlay(reference_image: str, sample: ReferenceSample, engine: EyeGeometry,
                                    alignment: ReferenceEngineAlignment, output_path: str) -> dict[str, float]:
    """Render reference pixels + approved traces + inverse-mapped engine + error segments."""
    from PIL import Image, ImageDraw
    image = Image.open(reference_image).convert("RGB")
    draw = ImageDraw.Draw(image)
    for curve in (sample.upper, sample.lower, sample.epicanthus):
        if curve:
            pts = [(round(x), round(y)) for x, y in curve.points_px]
            draw.line(pts, fill=(220, 30, 30), width=2)
    for ref_curve, engine_curve in ((sample.upper, engine.upper_lid_points), (sample.lower, engine.lower_lid_points)):
        if not ref_curve:
            continue
        mapped = [alignment.inverse_map(p) for p in engine_curve]
        draw.line([(round(x), round(y)) for x, y in mapped], fill=(30, 90, 220), width=2)
        ref_mapped = _resample(tuple(alignment.map(p) for p in ref_curve.points_px), len(engine_curve))
        for r, e in zip(ref_mapped, engine_curve):
            q = alignment.inverse_map(e); rr = alignment.inverse_map(r)
            draw.line([(round(q[0]), round(q[1])), (round(rr[0]), round(rr[1]))], fill=(180, 80, 180), width=1)
    for point in (sample.medial_terminal_px, sample.lateral_terminal_px):
        if point:
            draw.ellipse((point[0]-3, point[1]-3, point[0]+3, point[1]+3), fill=(220, 30, 30))
    image.save(output_path, optimize=False)
    return {"output": str(output_path), "width_px": image.width, "height_px": image.height}
