-- V1.3 state/effect precedence contract.
-- Data remains renderer-neutral; JSONB carries future state/effect payloads.

CREATE TABLE IF NOT EXISTS component_states (
    component_id TEXT NOT NULL REFERENCES components(component_id) ON DELETE CASCADE,
    state_name TEXT NOT NULL,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    priority INTEGER NOT NULL DEFAULT 0,
    exclusive_group TEXT,
    conflicts JSONB NOT NULL DEFAULT '[]'::jsonb,
    requires JSONB NOT NULL DEFAULT '[]'::jsonb,
    values JSONB NOT NULL DEFAULT '{}'::jsonb,
    PRIMARY KEY (component_id, state_name),
    CHECK (state_name <> ''),
    CHECK (exclusive_group IS NULL OR exclusive_group <> ''),
    CHECK (jsonb_typeof(conflicts) = 'array'),
    CHECK (jsonb_typeof(requires) = 'array'),
    CHECK (jsonb_typeof(values) = 'object')
);

CREATE INDEX IF NOT EXISTS idx_component_states_group_priority
    ON component_states(component_id, exclusive_group, priority DESC);

CREATE TABLE IF NOT EXISTS visual_effect_definitions (
    effect_id TEXT PRIMARY KEY,
    kind TEXT NOT NULL,
    priority INTEGER NOT NULL DEFAULT 0,
    alpha DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (alpha BETWEEN 0 AND 1),
    color TEXT NOT NULL DEFAULT '#000000',
    opacity_factor DOUBLE PRECISION NOT NULL DEFAULT 1 CHECK (opacity_factor BETWEEN 0 AND 1),
    visibility_factor DOUBLE PRECISION NOT NULL DEFAULT 1 CHECK (visibility_factor BETWEEN 0 AND 1),
    source_id TEXT NOT NULL DEFAULT '__external__',
    metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
    CHECK (effect_id <> ''),
    CHECK (kind <> ''),
    CHECK (source_id <> ''),
    CHECK (jsonb_typeof(metadata) = 'object')
);

CREATE TABLE IF NOT EXISTS component_effect_bindings (
    effect_id TEXT NOT NULL REFERENCES visual_effect_definitions(effect_id) ON DELETE CASCADE,
    target_component_id TEXT NOT NULL REFERENCES components(component_id) ON DELETE CASCADE,
    PRIMARY KEY (effect_id, target_component_id)
);

CREATE INDEX IF NOT EXISTS idx_component_effect_bindings_target
    ON component_effect_bindings(target_component_id, effect_id);
