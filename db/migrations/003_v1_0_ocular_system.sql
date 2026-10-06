-- V1.0 ocular system: bilateral lash tiers, eyelid fold contracts and expression intents.
CREATE TABLE IF NOT EXISTS ocular_lash_profiles (
    profile_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    tier TEXT NOT NULL CHECK (tier IN ('upper','lower')),
    style TEXT NOT NULL,
    values JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS ocular_eyelid_profiles (
    profile_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    values JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS ocular_expression_profiles (
    expression_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    intent TEXT NOT NULL UNIQUE,
    values JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_ocular_lash_profiles_tier ON ocular_lash_profiles(tier, style);
