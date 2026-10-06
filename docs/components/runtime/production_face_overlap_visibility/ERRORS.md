# Errors

`ERR-FOV-001`: V1.60 intentionally left owner extraction in `production_slice.py` to avoid mixing responsibilities. V1.62 later proved three real consumers and extracted that responsibility into its own owner.

`ERR-FOV-002`: the old production comment described occlusion proof as if it directly rewrote SVG.
Resolution: corrected the comment to distinguish resolved component visibility from parallel semantic occlusion proof.

`ERR-FOV-003`: monolithic `pytest -q` exceeded the available execution window without reporting a test failure.
Resolution: all 132 test files were executed in eight isolated deterministic groups; every group returned code 0, with the one documented PostgreSQL environment skip.
