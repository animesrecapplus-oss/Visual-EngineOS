# Adversarial test matrix — CMP-VBOOL-001

| ID | Attack | Expected | Evidence |
|---|---|---|---|
| ADV-VBOOL-001 | frozen result mutation | reject | dedicated truth test |
| ADV-VBOOL-002 | unsupported operation | reject | dedicated truth test |
| ADV-VBOOL-003 | negative ellipse radius | reject during materialization | dedicated truth test |
| ADV-VBOOL-004 | empty union | deterministic empty result | dedicated truth test |
| ADV-VBOOL-005 | disjoint intersection | zero-area result | dedicated truth test |
| ADV-VBOOL-006 | overlapping union | no double-count | visibility kernel regression |
| ADV-VBOOL-007 | hole-producing difference | preserve hole topology | dedicated truth test |
| ADV-VBOOL-008 | repeated identical operation | identical value | dedicated truth test |
| ADV-VBOOL-009 | public/legacy identity | single owner | dedicated truth test |
| ADV-VBOOL-010 | new dependency cycle | none | source audit |
| ADV-VBOOL-011 | exact duplicate implementation | none | source audit |
| ADV-VBOOL-012 | hot-path performance regression | measured, then corrected | benchmark |
