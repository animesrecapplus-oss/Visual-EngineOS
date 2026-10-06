"""Compatibility facade for ocular geometry construction.

Geometry construction is decomposed by responsibility under ``geometry/``:
shape factors, curves, contour, containment, lid-follow and final assembly.
"""
from .geometry.builder import build_eye_geometry


def build_binocular_eye_geometries(
    left_params=None, right_params=None, *, left_center=(-0.6, 0.0), right_center=(0.6, 0.0),
    target=(0.0, -1.0), left_state="normal", right_state="normal",
    left_appearance=None, right_appearance=None, strength=1.0, expression="neutral", amplitude=1.0,
):
    """Legacy binocular helper; each eye is solved independently against one target."""
    from .gaze.solver import BinocularGazeSolver, Gaze
    pair = BinocularGazeSolver.solve(left_center, right_center, target)
    left = build_eye_geometry(left_params, center=left_center, state=left_state,
        gaze=Gaze(target=target, strength=strength, amplitude=amplitude), appearance=left_appearance,
        expression=expression, side="image_left")
    right = build_eye_geometry(right_params, center=right_center, state=right_state,
        gaze=Gaze(target=target, strength=strength, amplitude=amplitude), appearance=right_appearance,
        expression=expression, side="image_right")
    return left, right, pair
