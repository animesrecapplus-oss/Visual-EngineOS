import threading

from visual_engine.components.face.eyes import EyeGeometryInputs, default_eye_geometry_registry
from visual_engine.model import Component
from visual_engine.runtime import CachedGeometryGenerator, GeometryCache, RuntimeGraph


def test_concurrent_cached_generation_reports_one_build_and_waiter_hits():
    graph = RuntimeGraph.from_component(Component("eye", "eye"))
    service = CachedGeometryGenerator(default_eye_geometry_registry(), GeometryCache(max_entries=8))
    inputs = EyeGeometryInputs()
    results = []
    barrier = threading.Barrier(2)

    def worker():
        barrier.wait(timeout=2)
        results.append(service.generate(graph, "eye", inputs=inputs))

    t1 = threading.Thread(target=worker)
    t2 = threading.Thread(target=worker)
    t1.start(); t2.start(); t1.join(); t2.join()
    assert len(results) == 2
    assert service.cache.stats().builds == 1
    assert sum(result.cache_hit for result in results) >= 1
    assert results[0].geometry is results[1].geometry
