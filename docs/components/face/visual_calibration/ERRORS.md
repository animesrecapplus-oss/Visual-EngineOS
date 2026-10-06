# Errors — CMP-FACE-VIS-001

- `ERR-FVIS-001`: first visual audit harness attempted to mutate frozen `Anchor`; corrected by replacing the anchor value object.
- `ERR-FVIS-002`: first test harness used wrong `Parameter` field names; corrected to `min_value`/`max_value`.
- `ERR-FVIS-003`: first hair detail prototype assigned a second depth layer to the same owner; production owner-depth extraction rejected it. Detail paths were moved to the existing hair depth layer.
- `ERR-FVIS-004`: first hair contour did not overlap ears enough; existing V1.63 relation test caught the regression. Side locks were extended and the test passed.
- `ERR-FVIS-005`: first V1.78 visual QA harness resolved its project root one directory too high; corrected and rerun with explicit root calculation.
- `ERR-FVIS-006`: the monolithic full regression exceeded the execution window; the same 1164 collected tests were rerun in deterministic batches, with all final batches passing.
- `ERR-FVIS-007`: one initial regression assertion still held the old head/ear overlap constants; measured post-correction values were recorded and the affected test was updated.
