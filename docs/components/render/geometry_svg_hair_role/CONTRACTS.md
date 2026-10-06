# Contracts — CMP-RENDER-GEOMETRY-SVG-HAIR-ROLE

`CON-GHR-001`: `hair` is a renderer role, not a Component-kind lookup.
`CON-GHR-002`: closed hair paths use resolved `style.fill`; open paths remain unfilled.
`CON-GHR-003`: priority 5 is after structural `head` priority 0 and before default detail priority 50.
`CON-GHR-004`: renderer never computes Hair appearance or geometry.
`CON-GHR-005`: visibility/opacity zero suppresses the path through the existing generic contract.
