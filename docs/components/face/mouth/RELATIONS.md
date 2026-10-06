# Relations — CMP-FACE-MOUTH

- `REL-MOUTH-PARENT-001`: `HumanFace → Mouth`; parent creates the child and supplies parameters/appearance.
- `REL-MOUTH-CACHE-001`: `Mouth → GeometryCache`; authored width/height participate in geometry identity.
- `REL-MOUTH-INPUT-001`: malformed `Component → Mouth leaf`; leaf rejects bypassed non-numeric/non-finite dimensions before geometry construction.
- `REL-MOUTH-RENDER-001`: `Mouth → GenericSVG`; renderer consumes the existing ellipse contract and resolved visual owner.
- `REL-MOUTH-VIS-001`: `Head → {Nose,Mouth}`; both are explicit depth-1 production occluders using the same camera-space geometry.
- `REL-MOUTH-APPEARANCE-001`: `HumanFace → Mouth visual`; mouth owns an explicit authored visual contract.
- `REL-MOUTH-PERSIST-001`: `Mouth → generic persistence`; component kind, parameters, anchor and visual payload round-trip without schema changes.

Direction remains acyclic after V1.81. No new SCC was introduced.
