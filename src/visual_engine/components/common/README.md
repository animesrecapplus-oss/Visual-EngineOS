# Common component infrastructure

This package owns contracts shared by every visual component.

Current implementation owners:

- `meta.py` — component metadata, parameters, anchors, relations and constraints;
- `visual_contract.py` — renderer-neutral visual/material/transform contracts;
- `geometry_contract.py` — renderer-neutral geometry/path/surface contracts.

The historical `visual_engine.model.*` modules are compatibility facades only. New shared component infrastructure belongs here.
