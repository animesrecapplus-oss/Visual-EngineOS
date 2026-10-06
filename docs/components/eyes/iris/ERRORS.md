# Iris error register — V1.84

`ERR-EYE-IRIS-001` — local numeric validation was permissive for bool count values and fractional count values.

`ERR-EYE-IRIS-002` — `outline_width=NaN` or infinity could pass the previous negative-only check.

`ERR-EYE-IRIS-003` — string numeric state produced an incidental `TypeError` rather than a controlled local validation
failure.

`ERR-EYE-IRIS-004` — renderer count fields are consumed by `range(...)`; accepting non-integer counts could defer a
local input defect into a downstream runtime failure.

Resolution: V1.84 moves these malformed states to the IrisSpec construction boundary without changing valid values.

`ERR-EYE-IRIS-005` — no maximum count is currently justified. This remains an explicit resource-risk boundary rather
than an invented limit.

`ERR-EYE-IRIS-006` — repository Git state is not verifiable from the checkpoint archive because `.git` metadata is absent.
Per the V1.84 protocol, this blocks final certification rather than being silently treated as clean.
