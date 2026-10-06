# Errors

`ERR-VDR-001`: previous implementation hard-coded `VisibilityRegionResult.depth_relation=FRONT` for every resolved front set.
Resolution: derive the result from the nearest participating occluder depth at lines 254-257.
