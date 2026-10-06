from __future__ import annotations

import math

from visual_engine.components.common.meta import Component
from visual_engine.components.face.eyes.geometry.view_axis import OcularBasis3D, OcularPose3D, compose_ocular_basis
from visual_engine.runtime.graph import RuntimeGraph


_OCULAR_PARAMETER_DEFAULTS = {
    "ocular_yaw_deg": 0.0,
    "ocular_pitch_deg": 0.0,
    "alignment_axis_rotation_deg": 0.0,
}


def _parameter_float(component: Component, name: str, default: float = 0.0) -> float:
    parameter = component.parameters.get(name)
    value = default if parameter is None else parameter.value
    if isinstance(value, bool):
        raise ValueError(f"ocular parameter {name} must be numeric")
    try:
        value = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"ocular parameter {name} must be numeric") from exc
    if not math.isfinite(value):
        raise ValueError(f"ocular parameter {name} must be finite")
    return value


def _ocular_pose(component: Component) -> OcularPose3D:
    """Interpret ocular parameters only at the eye-domain boundary.

    ``LocalTransform`` remains purely generic. Ocular orientation values are
    ordinary component parameters and acquire ocular meaning only here, inside
    the eye subsystem.
    """
    return OcularPose3D(
        yaw_deg=_parameter_float(component, "ocular_yaw_deg", _OCULAR_PARAMETER_DEFAULTS["ocular_yaw_deg"]),
        pitch_deg=_parameter_float(component, "ocular_pitch_deg", _OCULAR_PARAMETER_DEFAULTS["ocular_pitch_deg"]),
        roll_deg=float(component.transform.rotation_deg),
        alignment_axis_rotation_deg=_parameter_float(
            component,
            "alignment_axis_rotation_deg",
            _OCULAR_PARAMETER_DEFAULTS["alignment_axis_rotation_deg"],
        ),
    )


def resolve_ocular_basis(graph: RuntimeGraph, component_id: str) -> OcularBasis3D:
    """Resolve ocular orientation through the hierarchy at the eye boundary."""
    node = graph.get(component_id)
    chain: list[Component] = []
    current = node
    while True:
        chain.append(current.component)
        if current.parent_id is None:
            break
        current = graph.get(current.parent_id)
    chain.reverse()

    basis: OcularBasis3D | None = None
    for component in chain:
        basis = compose_ocular_basis(basis, _ocular_pose(component))
    if basis is None:  # pragma: no cover - graph.get guarantees a component
        raise ValueError("ocular basis resolution requires a component")
    return basis


def resolve_alignment_axis_rotation(graph: RuntimeGraph, component_id: str) -> float:
    """Accumulate the eye-domain alignment-axis parameter through the hierarchy."""
    node = graph.get(component_id)
    total = 0.0
    current = node
    while True:
        total += _parameter_float(current.component, "alignment_axis_rotation_deg")
        if current.parent_id is None:
            break
        current = graph.get(current.parent_id)
    if not math.isfinite(total):
        raise ValueError("resolved alignment-axis rotation must be finite")
    return total
