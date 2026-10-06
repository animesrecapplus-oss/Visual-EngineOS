from visual_engine.persistence.ocular_catalog import PostgresOcularCatalog
from visual_engine.runtime.catalog import CompiledProfileCache, ProfileKey


def test_profile_cache_compiles_once():
    cache = CompiledProfileCache()
    calls = []
    key = ProfileKey("lash", "anime_dense", 1)
    first = cache.get_or_compile(key, lambda: calls.append(1) or {"density": 1.0})
    second = cache.get_or_compile(key, lambda: calls.append(1) or {"density": 0.0})
    assert first is second
    assert calls == [1]


def test_profile_cache_can_invalidate_one_family():
    cache = CompiledProfileCache()
    cache.get_or_compile(ProfileKey("lash", "a", 1), lambda: 1)
    cache.get_or_compile(ProfileKey("pupil", "a", 1), lambda: 2)
    assert cache.invalidate(family="lash") == 1
    assert cache.get_or_compile(ProfileKey("pupil", "a", 1), lambda: 3) == 2


def test_catalog_query_is_single_versioned_indexed_lookup():
    sql = PostgresOcularCatalog.SQL
    assert "family = %s AND name = %s" in sql
    assert "active = TRUE" in sql
    assert "ORDER BY version DESC" in sql
    assert "LIMIT 1" in sql
