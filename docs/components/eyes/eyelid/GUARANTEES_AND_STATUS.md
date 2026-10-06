# CMP-EYE-EYELID — guarantees and status

## Guaranteed after V1.86

- local boolean controls are strict booleans;
- local numeric appearance controls are finite real values;
- existing numeric ranges remain enforced;
- valid authored values retain the previous downstream behavior;
- the value object remains frozen/slot-based;
- no cache, database, COLOR or renderer algorithm is changed.

## Not guaranteed by this brick

- anatomical eyelid quality;
- eyelid geometry fidelity;
- reference-calibrated crease proportions;
- gaze/occlusion correctness;
- visibility semantics beyond existing consumers;
- resource ceilings or performance optimization.

Status: `CERTIFIED` only for the local input-boundary scope after all V1.86 gates pass.
