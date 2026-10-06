from __future__ import annotations

"""Small deterministic cache for immutable component-resolution results.

V1.41 keeps this cache below the resolver and above fingerprint
construction.  A cache entry is valid only when the complete
``ResolutionFingerprint.cache_identity`` matches.  The cache never attempts to
reconstruct or compare partial visual state, and it never changes a resolved
component.  This makes cache invalidation a consequence of the existing
resolution dependency contract rather than a second, parallel dependency system.
"""

from collections import OrderedDict
from dataclasses import dataclass
from threading import Event, RLock
from typing import Callable

from visual_engine.runtime.versioning import ResolutionFingerprint


@dataclass(slots=True)
class _InFlightBuild:
    """State shared by callers coalescing one same-key resolution build."""

    event: Event
    value: object | None = None
    error: BaseException | None = None
    waiters: int = 0
    generation: int = 0


@dataclass(frozen=True, slots=True)
class ResolutionCacheStats:
    """Observable cache counters for deterministic QA and performance evidence."""

    hits: int = 0
    misses: int = 0
    stores: int = 0
    evictions: int = 0


class ResolutionCache:
    """Thread-safe bounded LRU cache keyed only by ``ResolutionFingerprint``.

    Ownership is deliberately explicit: this object is *caller-owned* and has no
    global, process, scene, or frame registry. The resolver accepts it by optional
    dependency injection; callers decide when to create, reuse, partition, and
    clear it. This keeps cache lifetime separate from graph lifetime until a real
    production renderer/scene owner exists.

    The cache stores immutable ``ResolvedComponent`` instances without importing
    the resolver itself, avoiding a dependency cycle. ``get_or_build`` is the
    production build boundary: it coalesces only identical fingerprints and leaves
    unrelated keys free to build concurrently.
    """

    def __init__(self, max_entries: int = 128) -> None:
        if not isinstance(max_entries, int) or isinstance(max_entries, bool) or max_entries < 1:
            raise ValueError("max_entries must be a positive integer")
        self.max_entries = max_entries
        self._entries: OrderedDict[str, object] = OrderedDict()
        self._lock = RLock()
        self._hits = 0
        self._misses = 0
        self._stores = 0
        self._evictions = 0
        self._generation = 0
        # Same-key concurrent MISSes are coalesced here.  The dictionary is
        # deliberately separate from LRU entries: in-flight work is transient
        # and must never consume cache capacity or become a stale cache entry.
        self._inflight: dict[str, _InFlightBuild] = {}

    def get(self, fingerprint: ResolutionFingerprint) -> object | None:
        """Return an exact-key match and record a hit/miss.

        The fingerprint object itself is not cached separately: its canonical
        SHA-256 identity is the complete key, so changed color/effect/context/
        version dependencies cannot reuse the old entry.
        """
        key = fingerprint.cache_identity
        with self._lock:
            value = self._entries.get(key)
            if value is None:
                self._misses += 1
                return None
            self._entries.move_to_end(key)
            self._hits += 1
            return value

    def put(self, fingerprint: ResolutionFingerprint, value: object) -> None:
        """Store one immutable resolution result under its complete identity."""
        key = fingerprint.cache_identity
        with self._lock:
            self._entries[key] = value
            self._entries.move_to_end(key)
            self._stores += 1
            while len(self._entries) > self.max_entries:
                evicted_key, _ = self._entries.popitem(last=False)
                self._evictions += 1
                flight = self._inflight.get(evicted_key)
                if flight is not None and flight.event.is_set():
                    self._inflight.pop(evicted_key, None)

    def get_or_build(
        self,
        fingerprint: ResolutionFingerprint,
        builder: Callable[[], object],
    ) -> tuple[object, bool]:
        """Return ``(value, reused)`` and coalesce concurrent same-key MISSes.

        The first caller that observes an absent key becomes the owner of the
        build. Later callers wait on the owner's event instead of rebuilding the
        same immutable resolution.  The owner publishes either a value or the
        exact build exception; no waiter can observe a half-written entry.
        """
        key = fingerprint.cache_identity
        while True:
            cached = self.get(fingerprint)
            if cached is not None:
                return cached, True

            with self._lock:
                # A caller can miss the first lookup, be descheduled while the
                # owner publishes, then arrive here after publication. Re-check
                # the entry before deciding whether a new flight is necessary.
                published = self._entries.get(key)
                if published is not None:
                    self._entries.move_to_end(key)
                    self._hits += 1
                    return published, True

                flight = self._inflight.get(key)
                if flight is None:
                    flight = _InFlightBuild(event=Event(), generation=self._generation)
                    self._inflight[key] = flight
                    owner = True
                else:
                    flight.waiters += 1
                    owner = False

            if not owner:
                # Never hold the cache lock while waiting for arbitrary resolver
                # work. This preserves unrelated-key parallelism.
                flight.event.wait()
                error = flight.error
                value = flight.value
                with self._lock:
                    flight.waiters -= 1
                    if flight.waiters == 0 and self._inflight.get(key) is flight:
                        self._inflight.pop(key, None)
                if error is not None:
                    raise error
                if value is not None:
                    return value, True
                # Defensive fallback: an implementation error must not silently
                # return an empty resolution. Re-enter and establish ownership.
                continue

            try:
                value = builder()
                # ``clear()`` advances the generation while an owner is building.
                # In that case the result remains valid for current waiters but is
                # deliberately not repopulated into the freshly cleared cache.
                with self._lock:
                    cache_generation = self._generation
                if flight.generation == cache_generation:
                    self.put(fingerprint, value)
            except BaseException as exc:
                with self._lock:
                    flight.error = exc
                    # Failed flights cannot safely remain reusable. Current waiters
                    # retain the flight object locally and receive the same error.
                    self._inflight.pop(key, None)
                    flight.event.set()
                raise
            else:
                with self._lock:
                    flight.value = value
                    # Current waiters retain the flight object locally. If there
                    # are none, remove the completed state immediately; a caller
                    # that missed just before publication will re-check the entry.
                    flight.event.set()
                    if flight.waiters == 0 and self._inflight.get(key) is flight:
                        self._inflight.pop(key, None)
                return value, False

    def clear(self) -> None:
        """Drop entries without altering cumulative diagnostic counters."""
        with self._lock:
            self._entries.clear()
            self._generation += 1
            # A clear is a lifecycle boundary. New callers must not join a build
            # that started before the boundary, while existing owner/waiter threads
            # keep their local flight object and can finish safely.
            self._inflight.clear()

    def __len__(self) -> int:
        with self._lock:
            return len(self._entries)

    @property
    def stats(self) -> ResolutionCacheStats:
        with self._lock:
            return ResolutionCacheStats(
                hits=self._hits,
                misses=self._misses,
                stores=self._stores,
                evictions=self._evictions,
            )
