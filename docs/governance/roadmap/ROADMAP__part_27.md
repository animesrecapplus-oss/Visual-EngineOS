# Roadmap — V1.71 and next frontier

## V1.71 — ProductionRenderSession lifecycle extraction

Fresh V1.70 audit first rejected `resolve_component_contract` again because static compatibility ownership creates a new cycle. The selected independent responsibility was the caller-owned `ProductionRenderSession` lifecycle boundary.

Canonical owner: `runtime/production_render_session.py:18-118`. `production_slice.py` is now a compatibility facade only.

Preserved: graph freshness/refresh, cache ownership, resource teardown, public identity, production delegation and all renderer-visible behavior.

Certified evidence includes focused hostile tests, full deterministic regression, compileall, dependency/cycle/duplicate audit, benchmark, real five-case visual QA, truth validation and ZIP integrity.

## V1.72 rule

Start from the fresh certified V1.71 checkpoint. Perform another read-only responsibility/consumer/contract/impact audit.
Do not assume the next production seam, resolver, cache, COLOR, persistence, renderer or compatibility wrapper without proof.
