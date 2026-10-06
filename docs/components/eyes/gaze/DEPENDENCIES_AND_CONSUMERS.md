# Dependencies and consumers — CMP-EYE-GAZE

## Direct owner dependencies

- `dataclasses.dataclass` — VERIFIED.
- `math` — VERIFIED.
- `numbers.Real` — V1.89 local validation dependency.
- `contracts.types.GazeDirection` — VERIFIED.
- `contracts.validation._finite` — VERIFIED and retained because `BinocularGazeSolver` uses it.

## Direct consumers

- `components/face/eyes/geometry/builder.py` — VERIFIED; `Gaze` reaches `GazeSolver`.
- `components/face/eyes/geometry/transform.py` — VERIFIED; transforms explicit targets and replaces the value.
- `components/face/eyes/generator.py` — VERIFIED; generator accepts `Gaze` and projects it into cache inputs.
- `components/face/eyes/pair.py` — VERIFIED; pair path constructs `Gaze` for both eyes.
- `components/face/eyes/geometry_builder.py` — VERIFIED compatibility/build helper.
- `components/face/eyes/definitions.py` and `geometry/__init__.py` — VERIFIED public compatibility exports.

## Indirect production path
`Gaze` → eye geometry builder/generator → renderer-neutral geometry → existing SVG production path.

No direct database serialization or migration consumer is verified.
