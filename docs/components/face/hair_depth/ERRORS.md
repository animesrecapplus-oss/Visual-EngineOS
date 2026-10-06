# Errors

`ERR-HD-001`: initial V1.58 adapter saw `hair_depth=0` because the V1.57 Hair surface was authored coplanar with Ear. This was a real semantic mismatch, not a test artifact.

Resolution: author Hair at `depth_layer=1` and retest the production path.

Status: resolved and covered by `TST-V158-001` and visual evidence.
