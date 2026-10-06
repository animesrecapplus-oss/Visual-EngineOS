# Pre-change impact audit

## Existing seam
`ProductionRenderSession.render_face` directly selected Head→Nose/Mouth occluders from the generator and
called `resolve_face_overlap_visibility` at the production boundary.

## Authorized extraction
One module, one responsibility: generator-specific production face-overlap orchestration.

## Checked before modification
- real consumer: confirmed at `production_slice.py:144-148` before edit;
- parent: ProductionRenderSession;
- siblings: owner geometry, visual styles, Hair/Ear, Head/Ear;
- leaf contract: production face-overlap visibility;
- cache/fingerprint: no new lookup or identity;
- persistence/DB: no path;
- COLOR: no consumer;
- determinism: mapping and tuple order fixed;
- visual: five-case identity required.

The impact audit was reopened after hostile testing exposed that the injected owner contract needed
explicit type/finite-depth validation at the new boundary. The implementation was corrected before
continuing certification.
