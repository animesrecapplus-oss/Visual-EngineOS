-- V1.3 generic component contract.
-- Relational/indexed fields are kept explicit; JSONB remains an extension point.

CREATE TABLE IF NOT EXISTS component_transforms (
    component_id TEXT PRIMARY KEY REFERENCES components(component_id) ON DELETE CASCADE,
    x DOUBLE PRECISION NOT NULL DEFAULT 0,
    y DOUBLE PRECISION NOT NULL DEFAULT 0,
    rotation_deg DOUBLE PRECISION NOT NULL DEFAULT 0,
    scale_x DOUBLE PRECISION NOT NULL DEFAULT 1,
    scale_y DOUBLE PRECISION NOT NULL DEFAULT 1,
    z DOUBLE PRECISION NOT NULL DEFAULT 0,
    CHECK (scale_x <> 0),
    CHECK (scale_y <> 0)
);

CREATE TABLE IF NOT EXISTS material_definitions (
    id BIGSERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    version INTEGER NOT NULL DEFAULT 1,
    roughness DOUBLE PRECISION NOT NULL DEFAULT 1 CHECK (roughness BETWEEN 0 AND 1),
    metallic DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (metallic BETWEEN 0 AND 1),
    transmission DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (transmission BETWEEN 0 AND 1),
    emission DOUBLE PRECISION NOT NULL DEFAULT 0 CHECK (emission BETWEEN 0 AND 1),
    payload JSONB NOT NULL DEFAULT '{}'::jsonb,
    UNIQUE(name, version)
);

CREATE TABLE IF NOT EXISTS component_visual_contracts (
    component_id TEXT PRIMARY KEY REFERENCES components(component_id) ON DELETE CASCADE,
    fill_color TEXT NOT NULL DEFAULT '#ffffff',
    contour_color TEXT NOT NULL DEFAULT '#000000',
    contour_width DOUBLE PRECISION NOT NULL DEFAULT 1 CHECK (contour_width >= 0),
    contour_opacity DOUBLE PRECISION NOT NULL DEFAULT 1 CHECK (contour_opacity BETWEEN 0 AND 1),
    contour_style TEXT NOT NULL DEFAULT 'solid',
    contour_cap TEXT NOT NULL DEFAULT 'round',
    contour_join TEXT NOT NULL DEFAULT 'round',
    material_id BIGINT REFERENCES material_definitions(id),
    opacity DOUBLE PRECISION NOT NULL DEFAULT 1 CHECK (opacity BETWEEN 0 AND 1),
    visibility DOUBLE PRECISION NOT NULL DEFAULT 1 CHECK (visibility BETWEEN 0 AND 1),
    payload JSONB NOT NULL DEFAULT '{}'::jsonb
);

CREATE INDEX IF NOT EXISTS idx_component_visual_material ON component_visual_contracts(material_id);
CREATE INDEX IF NOT EXISTS idx_material_definitions_name_version ON material_definitions(name, version);
