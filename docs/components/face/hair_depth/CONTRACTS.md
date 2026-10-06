# Contracts

`CON-HD-001`: Hair emits one closed `HAIR` surface.

`CON-HD-002`: that surface carries `depth_layer=1`.

`CON-HD-003`: Ear remains at `depth_layer=0` in its existing contract.

`CON-HD-004`: depth metadata is consumed by the existing generic visibility and renderer ordering paths; this micro-component does not implement either algorithm.

`CON-HD-005`: no database-specific representation is introduced; the depth is geometry output metadata.
