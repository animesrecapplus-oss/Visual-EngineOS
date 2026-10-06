# Guarantees and status — CMP-FACE-EYE-BILATERAL

Status: `CERTIFIED` for the bounded HumanFace production bilateral identity correction.

Certified:
- `left_eye` in the existing HumanFace production entity resolves to `image_left`;
- `right_eye` resolves to `image_right`;
- standalone/other Eye identities retain `single`;
- side reaches generated canthus/caruncle geometry;
- side participates in existing geometry cache input identity;
- Gaze, camera, COLOR, DB and renderer algorithms remain outside scope;
- final normal/boundary/interaction visual samples were produced and inspected.

Not certified:
- a generic side field for arbitrary Components;
- coordinate-derived side inference;
- generic prompt-driven bilateral resolution;
- generic clipping/mask integration;
- artistic universality beyond the existing HumanFace identity convention.
