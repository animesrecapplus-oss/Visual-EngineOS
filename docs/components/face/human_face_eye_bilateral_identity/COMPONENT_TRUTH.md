# Component truth — CMP-FACE-EYE-BILATERAL

## Identity
A production input-boundary correction preserving the already-authored bilateral identities of the two HumanFace Eye children.

## Responsibility
Map the existing stable HumanFace child identities `left_eye` and `right_eye` to the existing ocular `side` values before Eye geometry generation.

## Non-responsibility
No coordinate-based inference, generic scene-side inference, gaze solving, camera behavior, renderer behavior, clipping/mask, COLOR, persistence migration or prompt parsing.

## Authority
The existing HumanFace entity identity is authoritative for this bounded production mapping. The Eye generator remains the canonical input adapter; `EyeGeometryInputs.side` remains the downstream value.

## Inputs / outputs
Input: an `Eye` component with its existing `id` and `parent_id`.
Output: `EyeGeometryInputs.side` equal to `image_left`, `image_right` or historical `single` according to the bounded mapping contract.

## Lifecycle
HumanFace authoring → RuntimeGraph compilation → Eye default-input construction → geometry cache → Eye geometry → HumanFace composite → renderer.

## Guarantees
Only the existing HumanFace production identity mapping is certified. No universal bilateral identity system is claimed.
