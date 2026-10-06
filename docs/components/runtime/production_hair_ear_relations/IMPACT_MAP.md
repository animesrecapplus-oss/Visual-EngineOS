# Impact map

Affected production source:
- new canonical orchestration owner;
- `production_face_render.py` import/call site;
- runtime public export.

Affected tests: new V1.63 focused suite; existing V1.58 Hair/Ear tests remain unchanged semantically.

Parents/children/siblings: session lifecycle unchanged; Hair/Ear leaf unchanged; Head/Ear and face-overlap remain separate.

Cache/fingerprint: no new cache or fingerprint construction.

Persistence/database: no SQL, schema, migration or persistence consumer.

COLOR: no semantic change and no new COLOR consumer.

Visual behavior: exact V1.62 SVG identity is required; Hair/Ear semantic evidence must remain identical.
