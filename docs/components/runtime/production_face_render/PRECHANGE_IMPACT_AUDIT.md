# Pre-change impact audit

## VERIFY

Fresh certified V1.66 checkpoint was extracted. Status, roadmap, architecture, decisions, existing micro-component dossiers and current-only artifact policy were read. Workspace was clean before edits.

## ARCHITECT

Existing parent: `ProductionRenderSession`.
Existing seam: `render_face` owns resolution→generation→transform→style→SVG→relation calls plus result assembly.

The responsibility is independent from session lifecycle/cache ownership because all required services can be injected without moving ownership.

## IMPACT

Consumers: the public session method and its existing test/tool callers.

Children/siblings: generic resolution, geometry generation resources, transform, visual styles, SVG renderer, face-overlap, Hair/Ear, Head/Ear and owner-geometry owners.

Cache/fingerprint: no algorithm or owner change.

Persistence/database: no consumer found.

COLOR: no new downstream consumer found.

Determinism/visuals: render output can change if call order or inputs change, so exact V1.66 behavior and real visual QA are mandatory.

The audit was reopened after focused test failures when compatibility imports were temporarily lost; the final design restores the established compatibility surface.
