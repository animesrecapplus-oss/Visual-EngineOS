# ResolutionContext — component truth

`CMP-RUNTIME-RESOLUTION-CONTEXT` is the canonical owner of the immutable external input contract used by generic resolution.

Owner: `src/visual_engine/runtime/resolution_context.py:10-97`.
Parent: generic resolution path in `runtime/contract.py`.
Production consumers: production face render, production visual styles, production session; consequence binding retains the compatibility facade because its lazy import is a cycle-avoidance boundary.
Public compatibility: `runtime/__init__.py:7-8`; `runtime/contract.py:27` re-exports the same object.

The owner validates/canonicalizes context only. State/effect semantics, fingerprinting, caches, rendering, persistence and database behavior remain elsewhere.
