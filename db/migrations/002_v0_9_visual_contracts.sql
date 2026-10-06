-- V0.9 visual contracts: component-level color/contour and explicit presentation profiles.
CREATE TABLE IF NOT EXISTS component_visual_styles (
    component_id TEXT PRIMARY KEY REFERENCES components(component_id) ON DELETE CASCADE,
    fill_color TEXT,
    contour_color TEXT NOT NULL DEFAULT '#000000',
    contour_width DOUBLE PRECISION NOT NULL DEFAULT 0.018 CHECK (contour_width >= 0),
    contour_style TEXT NOT NULL DEFAULT 'solid',
    style_metadata JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE TABLE IF NOT EXISTS ocular_presentation_profiles (
    profile_id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    age_group TEXT NOT NULL,
    presentation TEXT NOT NULL,
    values JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_component_visual_styles_contour ON component_visual_styles(contour_color, contour_style);
