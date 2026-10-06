# Decision register — V1.56

## D-108 — HumanFace Ear production family

Ear is the next production family because the V1.47 overlap gate was already proven and V1.55 established a real Mouth production child. The existing Ear children were otherwise only declarative.

## D-109 — renderer EAR role boundary

The existing renderer rejects negative depth. V1.56 therefore keeps `depth_layer=0` and adds only the explicit `ear` fill/paint priority required to place Ear behind the structural head. No negative-depth semantics are introduced.

## D-110 — compatibility

The V1.55 `face.human_with_eyes_nose_mouth` generator remains available explicitly. Only the default production request advances to the ear-inclusive generator.

## D-111 — COLOR/database frozen

No new COLOR downstream consumer or persistence schema consumer was demonstrated; both remain unchanged.

## D-112 — performance

The measured V1.55→V1.56 warm-render change is retained as evidence. No speculative cache or optimization was introduced.
