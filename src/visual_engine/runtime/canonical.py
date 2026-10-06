"""Compatibility import for deterministic canonicalization.

The canonicalizer is a model-layer primitive, so its implementation lives in
``components.common`` and can be used without importing runtime modules.
"""
from visual_engine.components.common.canonical import canonicalize

__all__ = ["canonicalize"]
