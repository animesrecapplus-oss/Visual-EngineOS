# V1.79 — Face granularity matrix

## Purpose

This matrix operationalizes the permanent vision's recursive atomicity without declaring blueprint items implemented. A row is `REAL` only when an executable owner and real consumer are verified.

| Region / micro-component | Current truth | Canonical owner | Real consumer | Status | Next boundary |
|---|---|---|---|---|---|
| HumanFace | component + authoring root | `entities/face.py:4-51` | production session | REAL | preserve root ownership |
| Head geometry | embedded `HEAD` surface | `components/face/generators.py:58-104` | face composites | REAL / EMBEDDED | possible standalone cranial/face split only with consumer |
| Cranial volume | no separate component | none | none | PLANNED | define boundary against face surface |
| Face surface | currently represented by `HEAD` | HumanFace generator | visibility/render | REAL / COARSE | semantic regionalization later |
| Eye | deep atomic system | `components/face/eyes/*` | face composites | REAL / DEEP | continue breadth-first rotation |
| Nose | production leaf | `generators.py:231-306` | face composites | REAL / DOSSIER ADDED V1.79 | future nasal subregions only with evidence |
| Mouth | production leaf | `components/face/mouth.py:1-52` | mouth/ear/hair composites | REAL | oral region boundary |
| Oral region | no separate owner | none | none | PLANNED | relation between nose/mouth/chin |
| Ear | production leaf | `components/face/ear.py:1-56` | ear composite | REAL | inner-ear morphology later |
| Hair | bounded silhouette/detail | `components/face/hair.py:1-87` | hair composite / Hair-Ear relation | REAL / COARSE | scalp boundary then hairline |
| Hair depth | explicit micro-component | dossier `face/hair_depth` | renderer/relation path | REAL | keep separate |
| Scalp boundary | no separate owner | none | none | PLANNED | cranial surface attachment |
| Hairline | parameter only, not semantic owner | `hair.py` parameter | none as standalone | PLANNED | geometric boundary contract |
| Hair mass sections | no standalone owners | none | none | PLANNED | crown/temporal/frontal/occipital sections |
| Hair locks/groups | no standalone owners | none | none | PLANNED | flow/grouping |
| Hair strands | no strand anatomy owner | none | none | PLANNED | only after mass/section boundary |
| Chin | no separate component | embedded head geometry | none | PLANNED | jaw/chin boundary |
| Cheeks | no separate component | embedded head geometry | none | PLANNED | facial surface regions |
| Forehead | no separate component | embedded head geometry | none | PLANNED | cranial/face transition |

## Interpretation

`PLANNED` is not `IMPLEMENTED`. Empty speculative source directories are intentionally not created.
The matrix is a selection map for future micro-component dossiers and horizontal development.

## V1.81 update — Mouth leaf boundary

`Mouth` remains a real leaf. V1.81 hardens its input boundary only; no oral-region child is promoted.
`OralRegion`, lips, commissures and mental/chin subregions remain `PLANNED` until independent executable owners and consumers exist.
