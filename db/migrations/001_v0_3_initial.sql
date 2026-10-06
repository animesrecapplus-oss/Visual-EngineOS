CREATE TABLE IF NOT EXISTS schema_versions (
    schema_version TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS component_types (
    component_type_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    description TEXT
);

CREATE TABLE IF NOT EXISTS entity_instances (
    entity_id TEXT PRIMARY KEY,
    schema_version TEXT NOT NULL,
    payload JSONB NOT NULL
);

CREATE TABLE IF NOT EXISTS entity_versions (
    entity_version_id BIGSERIAL PRIMARY KEY,
    entity_id TEXT NOT NULL REFERENCES entity_instances(entity_id) ON DELETE CASCADE,
    version INTEGER NOT NULL,
    engine_version TEXT NOT NULL,
    seed BIGINT NOT NULL,
    payload JSONB NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE(entity_id, version)
);

CREATE TABLE IF NOT EXISTS components (
    component_id TEXT PRIMARY KEY,
    entity_id TEXT NOT NULL REFERENCES entity_instances(entity_id) ON DELETE CASCADE,
    parent_id TEXT REFERENCES components(component_id) ON DELETE CASCADE,
    component_type_id BIGINT REFERENCES component_types(component_type_id),
    kind TEXT NOT NULL,
    parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    anchors JSONB NOT NULL DEFAULT '{}'::jsonb,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS relations (
    relation_id BIGSERIAL PRIMARY KEY,
    entity_id TEXT NOT NULL REFERENCES entity_instances(entity_id) ON DELETE CASCADE,
    source_id TEXT NOT NULL REFERENCES components(component_id) ON DELETE CASCADE,
    relation_type TEXT NOT NULL,
    target_id TEXT NOT NULL REFERENCES components(component_id) ON DELETE CASCADE,
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS constraints (
    constraint_id BIGSERIAL PRIMARY KEY,
    component_id TEXT NOT NULL REFERENCES components(component_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,
    expression TEXT NOT NULL,
    weight DOUBLE PRECISION NOT NULL DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS profiles (
    profile_id BIGSERIAL PRIMARY KEY,
    component_id TEXT REFERENCES components(component_id) ON DELETE CASCADE,
    profile_type TEXT NOT NULL,
    name TEXT NOT NULL,
    values JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS appearance_layers (
    appearance_layer_id BIGSERIAL PRIMARY KEY,
    component_id TEXT NOT NULL REFERENCES components(component_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    values JSONB NOT NULL DEFAULT '{}'::jsonb,
    opacity DOUBLE PRECISION NOT NULL DEFAULT 1.0
);

CREATE TABLE IF NOT EXISTS state_layers (
    state_layer_id BIGSERIAL PRIMARY KEY,
    component_id TEXT NOT NULL REFERENCES components(component_id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    values JSONB NOT NULL DEFAULT '{}'::jsonb,
    enabled BOOLEAN NOT NULL DEFAULT TRUE
);

CREATE TABLE IF NOT EXISTS scene_instances (
    scene_instance_id TEXT PRIMARY KEY,
    schema_version TEXT NOT NULL,
    frame_width INTEGER NOT NULL,
    frame_height INTEGER NOT NULL,
    camera JSONB NOT NULL DEFAULT '{}'::jsonb,
    policy JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS placements (
    scene_instance_id TEXT NOT NULL REFERENCES scene_instances(scene_instance_id) ON DELETE CASCADE,
    entity_id TEXT NOT NULL REFERENCES entity_instances(entity_id),
    x DOUBLE PRECISION NOT NULL,
    y DOUBLE PRECISION NOT NULL,
    z DOUBLE PRECISION NOT NULL DEFAULT 0,
    scale DOUBLE PRECISION NOT NULL DEFAULT 1,
    rotation DOUBLE PRECISION NOT NULL DEFAULT 0,
    PRIMARY KEY(scene_instance_id, entity_id)
);

CREATE INDEX IF NOT EXISTS idx_components_entity ON components(entity_id);
CREATE INDEX IF NOT EXISTS idx_components_parent ON components(parent_id);
CREATE INDEX IF NOT EXISTS idx_relations_entity ON relations(entity_id);
CREATE INDEX IF NOT EXISTS idx_entity_versions_entity ON entity_versions(entity_id);
