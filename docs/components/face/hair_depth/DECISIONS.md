# Decisions

`DEC-HD-001`: change Hair depth from `0` to `1` in V1.58.

Evidence: V1.57 production geometry has measurable Hair/Ear intersection; Hair already paints after Ear. Keeping both coplanar made semantic occlusion report `COPLANAR` or no blocking despite visual foreground order.

`DEC-HD-002`: do not alter Ear depth.

`DEC-HD-003`: do not modify the generic coverage/visibility kernel.
