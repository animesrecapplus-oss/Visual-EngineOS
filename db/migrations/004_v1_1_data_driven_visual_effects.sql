-- V1.1: declarative visual-effect catalog.
-- PostgreSQL is a cold-path source of truth; the renderer uses compiled memory objects.

CREATE TABLE IF NOT EXISTS ocular_profile_bundles (
    profile_id BIGSERIAL PRIMARY KEY,
    family TEXT NOT NULL,
    name TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version > 0),
    active BOOLEAN NOT NULL DEFAULT TRUE,
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    UNIQUE (family, name, version)
);

CREATE INDEX IF NOT EXISTS idx_ocular_profile_lookup
    ON ocular_profile_bundles (family, name, active, version DESC);

CREATE TABLE IF NOT EXISTS ocular_effect_definitions (
    effect_id BIGSERIAL PRIMARY KEY,
    family TEXT NOT NULL,
    name TEXT NOT NULL,
    effect_type TEXT NOT NULL,
    version INTEGER NOT NULL CHECK (version > 0),
    parameters JSONB NOT NULL DEFAULT '{}'::jsonb,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    UNIQUE (family, name, version)
);

CREATE INDEX IF NOT EXISTS idx_ocular_effect_lookup
    ON ocular_effect_definitions (family, name, active, version DESC);

-- The bundle is intentionally JSONB because effect parameters evolve faster than
-- relational structure. Stable lookup identity/version remains relational and indexed.
-- This is controlled JSONB, not an opaque entity blob.
