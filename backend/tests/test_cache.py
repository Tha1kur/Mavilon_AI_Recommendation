from datetime import datetime, timedelta
import services.cache_service as module


def test_cache_expiry_without_sleep(monkeypatch):
    class Clock:
        now = datetime(2026, 1, 1)
        @classmethod
        def utcnow(cls):
            return cls.now
    monkeypatch.setattr(module, "datetime", Clock)
    cache = module.CacheService()
    assert cache.get("missing") is None
    cache.set("item", {"title": "Fixture"}, ttl=5)
    assert cache.get("item") == {"title": "Fixture"}
    Clock.now += timedelta(seconds=6)
    assert cache.get("item") is None
    assert cache.get_stats()["total_keys"] == 0


def test_invalidation_is_scoped_and_clear_removes_all():
    cache = module.CacheService()
    cache.set("a", 1)
    cache.set("b", 2)
    cache.invalidate("a")
    assert cache.get("a") is None
    assert cache.get("b") == 2
    cache.clear()
    assert cache.get("b") is None
