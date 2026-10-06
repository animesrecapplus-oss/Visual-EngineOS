# Architecture Principles — Non-Negotiable Rules

## P01 — Description before pixels
The canonical source of truth is a structured visual representation. Rendering is downstream.

## P02 — Geometry is not appearance
A geometry generator must not become the material/color/lighting engine.

## P03 — Structure is not style
A character's anatomical/structural model must survive style changes.

## P04 — Appearance is compositional
Base color, material, light, shadow, transmission, reflection and style response combine to produce effective appearance.

## P05 — Generic systems stay generic
Occlusion, visibility, interaction, color, caching and composition must not become lists of object names.

## P06 — Partial coverage is normal
Visibility is continuous and region-based, not simply visible/hidden.

## P07 — Geometry first, semantic consequences second
For interactions, resolve geometric location first, then affected semantic regions and consequences.

## P08 — Identity is persistent
Regenerating a character from the same scene position must not silently create a different character.

## P09 — Determinism is a feature
Seeds, versions and provenance must make important generation decisions reproducible.

## P10 — Cache only what is actually invariant
Visual-only changes must not invalidate geometry unnecessarily.

## P11 — The eye is a stress test, not the architecture
Eye-specific code may validate generic infrastructure but must not define universal contracts.

## P12 — Prototype is not production
Structural SVG demonstrations must never be described as final artistic quality.

## P13 — Prefer explicit contracts
When a subsystem crosses a boundary, use a typed/structured contract rather than hidden side effects.

## P14 — No premature abstraction
An abstraction must solve a real repeated problem and have a testable contract.

## P15 — No premature optimization
Measure before moving work to GPU or introducing complexity for theoretical performance.

## P16 — Every important behavior needs a test
If a behavior matters visually or architecturally, encode it as a deterministic test and, where applicable, a visual regression case.

## P17 — Future animation must remain possible
Current data models should not make time-dependent geometry/state impossible, even if animation is implemented later.

## P18 — Consult the master vision before extending the engine
When a local implementation conflicts with the general visual-language architecture, the general architecture wins unless a documented decision changes the vision.
