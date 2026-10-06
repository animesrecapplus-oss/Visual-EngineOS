# Relations

`REL-GSR-001`: `ProductionRenderSession.__init__` in `production_render_session.py:25-41` → geometry-service resource owner; direction is parent → child.

`REL-GSR-002`: resource owner → existing `CachedGeometryGenerator`; service semantics remain downstream.

`REL-GSR-003`: resource owner → supplied `GeometryCache`; dependency only, ownership remains with session.

`REL-GSR-004`: session `render_face` in `production_render_session.py:63-92` → resource `geometry_service.generate`; the call replaces the previous direct
session-owned service field without changing arguments or output.

`REL-GSR-005`: session `close` in `production_render_session.py:100-118` → resource `close`; cache clearing remains in session before resource release.

`REL-GSR-006`: relation/visual siblings remain independent and retain their existing canonical owners.
