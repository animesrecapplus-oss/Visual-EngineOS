# Invariants and assumptions

`INV-HEO-001`: target and occluder owner ids are distinct.

`INV-HEO-002`: exactly one semantic area region exists for each bounded Hair/Ear owner.

`INV-HEO-003`: opacity and transmission are finite and in `[0,1]`.

`INV-HEO-004`: Hair depth `1` is in front of Ear depth `0` in the certified production face.

`INV-HEO-005`: hidden Hair can have geometric overlap while producing no optical loss because its forwarded opacity is zero.

Assumption: the current Hair cap is the intended foreground occluder where the measured overlap exists.
