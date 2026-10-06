# Decisions

`DEC-FOV-001`: extract only the existing Head→Nose/Mouth visibility responsibility; no second production concern is moved.
`DEC-FOV-002`: inject the canonical `extract_production_owner_geometry` callable rather than duplicate extraction or create a reverse dependency.
`DEC-FOV-003`: preserve `ProductionVisibilityResolution` as the canonical result type and retain the existing runtime export.
`DEC-FOV-004`: expose the canonical resolver publicly because the extracted owner is now the unique callable boundary.
`DEC-FOV-005`: no visual algorithm change is permitted; exact SVG identity is a release gate.
