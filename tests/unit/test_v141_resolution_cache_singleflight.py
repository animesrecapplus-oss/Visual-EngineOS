from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from threading import Barrier, Event, Lock
from time import monotonic, sleep

import pytest

from visual_engine.components.common.meta import Component
from visual_engine.model import VisualContract
from visual_engine.runtime.contract import ResolutionContext, resolve_component
from visual_engine.runtime.graph import RuntimeGraph
from visual_engine.runtime.resolution_cache import ResolutionCache
from visual_engine.runtime.versioning import VersionStamp, resolution_fingerprint


@dataclass(frozen=True, slots=True)
class _Key:
    cache_identity: str


def _graph() -> RuntimeGraph:
    root = Component("root", "root", visual=VisualContract(fill_color="#607080"))
    face = Component("face", "face")
    sibling = Component("sibling", "sibling")
    root.add_child(face)
    root.add_child(sibling)
    return RuntimeGraph.from_component(root)


def _fp(graph: RuntimeGraph, component_id: str = "face"):
    return resolution_fingerprint(graph, component_id, ResolutionContext(), VersionStamp())


class _BarrierMissCache(ResolutionCache):
    """Force all same-key callers through MISS before ownership is selected."""

    def __init__(self, workers: int):
        super().__init__(max_entries=8)
        self.miss_barrier = Barrier(workers)
        self.put_count = 0
        self._count_lock = Lock()

    def get(self, fingerprint):
        value = super().get(fingerprint)
        if value is None:
            self.miss_barrier.wait(timeout=5)
        return value

    def put(self, fingerprint, value):
        with self._count_lock:
            self.put_count += 1
        super().put(fingerprint, value)


def test_same_key_concurrent_resolver_miss_builds_once_and_shares_immutable_result():
    graph = _graph()
    workers = 16
    cache = _BarrierMissCache(workers)
    context = ResolutionContext()

    with ThreadPoolExecutor(max_workers=workers) as pool:
        values = list(pool.map(
            lambda _: resolve_component(graph, "face", context=context, cache=cache),
            range(workers),
        ))

    assert cache.put_count == 1
    assert cache.stats.misses == workers
    assert cache.stats.stores == 1
    assert len({id(value) for value in values}) == 1
    assert all(value.visual == values[0].visual for value in values)
    assert all(value.provenance == values[0].provenance for value in values)


def test_singleflight_owner_and_waiter_preserve_cache_hit_semantics_after_publish():
    cache = ResolutionCache(max_entries=2)
    fingerprint = _Key("same")
    builds = 0
    lock = Lock()

    def builder():
        nonlocal builds
        with lock:
            builds += 1
        sleep(.01)
        return object()

    barrier = Barrier(8)
    def call():
        barrier.wait(timeout=5)
        return cache.get_or_build(fingerprint, builder)

    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(lambda _: call(), range(8)))

    assert builds == 1
    assert len({id(value) for value, _ in results}) == 1
    assert sum(reused for _, reused in results) == 7
    value, reused = cache.get_or_build(fingerprint, builder)
    assert reused is True
    assert value is results[0][0]
    assert builds == 1
    assert cache.stats.stores == 1


def test_singleflight_propagates_same_builder_failure_to_waiters_without_deadlock():
    cache = ResolutionCache(max_entries=2)
    fingerprint = _Key("failure")
    workers = 8
    barrier = Barrier(workers)
    builder_started = Event()
    release_failure = Event()
    calls = 0
    lock = Lock()

    def builder():
        nonlocal calls
        with lock:
            calls += 1
        builder_started.set()
        assert release_failure.wait(timeout=5)
        raise ValueError("resolution build failed")

    def call():
        barrier.wait(timeout=5)
        try:
            cache.get_or_build(fingerprint, builder)
        except ValueError as exc:
            return str(exc)
        raise AssertionError("builder failure was not propagated")

    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(call) for _ in range(workers)]
        assert builder_started.wait(timeout=5)
        # Give the remaining callers a deterministic window to join the active
        # flight before the owner publishes its failure.
        sleep(.02)
        release_failure.set()
        messages = [future.result(timeout=5) for future in futures]

    assert calls == 1
    assert messages == ["resolution build failed"] * workers
    assert len(cache) == 0
    assert cache.stats.stores == 0
    assert cache.stats.evictions == 0
    assert not cache._inflight


def test_failed_key_can_be_rebuilt_by_a_later_caller():
    cache = ResolutionCache(max_entries=2)
    fingerprint = _Key("retry")
    attempts = 0

    def builder():
        nonlocal attempts
        attempts += 1
        if attempts == 1:
            raise RuntimeError("first attempt")
        return "success"

    with pytest.raises(RuntimeError, match="first attempt"):
        cache.get_or_build(fingerprint, builder)
    value, reused = cache.get_or_build(fingerprint, builder)
    assert value == "success"
    assert reused is False
    assert attempts == 2
    assert cache.stats.stores == 1


def test_distinct_keys_build_in_parallel_without_global_singleflight_serialization():
    cache = ResolutionCache(max_entries=4)
    keys = [_Key("a"), _Key("b")]
    started = Barrier(2)
    finished = Barrier(2)
    active = 0
    peak_active = 0
    lock = Lock()

    def builder_for(key):
        nonlocal active, peak_active
        with lock:
            active += 1
            peak_active = max(peak_active, active)
        started.wait(timeout=5)
        finished.wait(timeout=5)
        with lock:
            active -= 1
        return key.cache_identity

    def call(key):
        return cache.get_or_build(key, lambda: builder_for(key))

    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(pool.map(call, keys))
    assert results == [("a", False), ("b", False)]
    assert peak_active == 2


def test_completed_inflight_state_is_released_and_lru_remains_bounded():
    cache = ResolutionCache(max_entries=1)
    first = _Key("first")
    second = _Key("second")
    cache.get_or_build(first, lambda: object())
    assert not cache._inflight
    cache.get_or_build(second, lambda: object())
    assert len(cache) == 1
    assert not cache._inflight




def test_clear_during_active_build_does_not_repopulate_cache_after_lifecycle_boundary():
    cache = ResolutionCache(max_entries=2)
    fingerprint = _Key("clear-race")
    builder_started = Event()
    release_builder = Event()

    def builder():
        builder_started.set()
        assert release_builder.wait(timeout=5)
        return object()

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(cache.get_or_build, fingerprint, builder)
        assert builder_started.wait(timeout=5)
        cache.clear()
        release_builder.set()
        value, reused = future.result(timeout=5)

    assert reused is False
    assert value is not None
    assert len(cache) == 0
    assert cache.get(fingerprint) is None
    assert not cache._inflight

def test_clear_removes_completed_flights_but_does_not_cancel_active_build():
    cache = ResolutionCache(max_entries=2)
    first = _Key("first")
    cache.get_or_build(first, lambda: object())
    cache.clear()
    assert len(cache) == 0
    assert not cache._inflight




def test_caller_owned_cache_can_be_handed_to_a_new_frame_without_global_ownership():
    cache = ResolutionCache(max_entries=8)
    frame_one_graph = _graph()
    frame_one = resolve_component(frame_one_graph, "face", cache=cache)

    # A new frame compiles a fresh RuntimeGraph from the same authoring scene.
    # No global cache is introduced; the caller explicitly hands the same cache
    # object to the next frame. The immutable result can be shared because its
    # complete fingerprint identity remains unchanged.
    frame_two_graph = frame_one_graph.rebuild()
    frame_two = resolve_component(frame_two_graph, "face", cache=cache)

    assert frame_two is frame_one
    assert cache.stats.misses == 1
    assert cache.stats.hits == 1
    assert frame_two.visual == frame_one.visual
    assert frame_two.provenance == frame_one.provenance

def test_stale_graph_guard_runs_before_singleflight_lookup():
    graph = _graph()
    cache = ResolutionCache(max_entries=4)
    resolve_component(graph, "face", cache=cache)
    graph.get("root").component.add_child(Component("new", "sibling"))

    class SpyCache(ResolutionCache):
        def __init__(self):
            super().__init__(max_entries=4)
            self.called = False

        def get_or_build(self, fingerprint, builder):
            self.called = True
            return super().get_or_build(fingerprint, builder)

    spy = SpyCache()
    with pytest.raises(RuntimeError, match="stale"):
        resolve_component(graph, "face", cache=spy)
    assert spy.called is False


def test_uncached_resolution_remains_equal_to_cached_resolution():
    graph = _graph()
    context = ResolutionContext()
    uncached = resolve_component(graph, "face", context=context)
    cache = ResolutionCache(max_entries=4)
    cached = resolve_component(graph, "face", context=context, cache=cache)
    assert cached.visual == uncached.visual
    assert cached.geometry == uncached.geometry
    assert cached.trace == uncached.trace
    assert cached.provenance == uncached.provenance
    assert cached.fingerprint == uncached.fingerprint


def test_singleflight_wait_does_not_hold_cache_lock_for_unrelated_key():
    cache = ResolutionCache(max_entries=4)
    first = _Key("first")
    second = _Key("second")
    owner_started = Barrier(2)
    release_owner = Barrier(2)

    def slow_builder():
        owner_started.wait(timeout=5)
        release_owner.wait(timeout=5)
        return "first"

    with ThreadPoolExecutor(max_workers=2) as pool:
        owner_future = pool.submit(cache.get_or_build, first, slow_builder)
        owner_started.wait(timeout=5)
        t0 = monotonic()
        value, reused = cache.get_or_build(second, lambda: "second")
        elapsed = monotonic() - t0
        release_owner.wait(timeout=5)
        owner_value, owner_reused = owner_future.result(timeout=5)

    assert value == "second"
    assert reused is False
    assert owner_value == "first"
    assert owner_reused is False
    assert elapsed < .5
