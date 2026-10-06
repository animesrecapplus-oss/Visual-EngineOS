-- Deterministic baseline catalog entries. These are data, not renderer branches.
INSERT INTO ocular_profile_bundles (family, name, version, payload)
VALUES
('lash', 'human_default', 1, '{"upper":{"density":0.82,"length":0.12,"thickness":0.018,"form":"line"},"shadow":{"opacity":0.18,"density_response":0.72,"thickness_response":0.58,"length_response":0.34},"lower":{"density":0.28,"length":0.055,"thickness":0.008,"opacity":0.34,"form":"line"}}'::jsonb),
('lash', 'anime_dense', 1, '{"upper":{"density":0.98,"length":0.15,"thickness":0.022,"form":"tapered"},"lower":{"density":0.22,"length":0.045,"thickness":0.006,"opacity":0.28,"form":"line"}}'::jsonb),
('pupil', 'glow_headlight', 1, '{"glow":{"enabled":true,"intensity":1.0,"radius":2.2,"blur":0.18,"core_intensity":1.0,"core_radius":0.55}}'::jsonb),
('pupil', 'smoke_upward', 1, '{"smoke":{"enabled":true,"opacity":0.6,"length":0.45,"width":0.08,"curl":0.18,"direction_deg":-90.0,"wisps":3}}'::jsonb)
ON CONFLICT (family, name, version) DO NOTHING;
