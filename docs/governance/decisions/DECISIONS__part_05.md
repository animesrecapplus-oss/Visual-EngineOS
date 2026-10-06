# Decision register — V1.55

## D-103 — V1.55 real Mouth production integration

The next production brick after V1.54 is `HumanFace/Mouth`, because V1.47 already proved one real overlapping face pair
and V1.46 explicitly deferred further face families only until that evidence existed.

The existing generic ellipse primitive is reused. No mouth-specific renderer branch is introduced.

## D-104 — production registry extension boundary

Historical `default_face_geometry_registry()` remains stable. `production_face_geometry_registry()` owns only the
V1.55 production extension. This avoids a new dependency cycle between the historical generator module and the new
composite owner while preserving existing public generator behaviour.

## D-105 — explicit multi-occluder production request

The existing renderer-independent visibility kernel already supports multiple occluders. V1.55 passes the real
Nose and Mouth regions together instead of creating another occlusion implementation.

## D-106 — performance regression is evidence, not a hidden optimization target

The measured visibility/render increase is retained. A cache or other optimization is not added without a demonstrated
lifetime/invalidation consumer and a measured need.

## D-107 — COLOR and database remain frozen

No COLOR semantic consumer was introduced by this brick and no persistence schema consumer required a migration.
