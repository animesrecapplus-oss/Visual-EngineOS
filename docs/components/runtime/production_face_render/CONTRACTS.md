# Contracts

`CON-PFR-001`: root, graph, service resources and resolution cache are concrete runtime objects supplied by the session owner.

`CON-PFR-002`: component ID and generator are non-empty strings; context/version are typed when supplied.

`CON-PFR-003`: generic resolution occurs through the canonical `resolve_component` owner and the supplied caller-owned cache.

`CON-PFR-004`: geometry generation occurs through the session's existing `CachedGeometryGenerator` resource owner.

`CON-PFR-005`: camera/scene geometry uses the canonical `resolve_geometry_contract` path.

`CON-PFR-006`: renderer-visible styles use the existing production visual-style owner and the already-resolved root visual.

`CON-PFR-007`: SVG uses the existing `render_geometry_svg` implementation; no renderer semantics move here.

`CON-PFR-008`: overlap and Ear relations delegate to their existing semantic/orchestration owners without duplicated algorithms.

`CON-PFR-009`: the producer returns the canonical `ProductionRenderResult` type without reconstructing a second result class.
