import os
import pytest


@pytest.mark.skipif(
    not os.getenv("LETTA_URL", "").startswith("http"),
    reason="LETTA_URL not set to real server"
)
def test_letta_store_write_and_recall():
    import time
    from backend.app.memory.service import LettaStore

    letta_url = os.getenv("LETTA_URL", "http://localhost:8283")
    store = LettaStore(letta_url)
    assert store.available, f"LettaStore not available at {letta_url}"

    user_id = f"test-u-{int(time.time())}"
    mid = store.write(user_id=user_id, content="我喜欢喝美式咖啡，住在上海")
    assert mid, "write should return an id"

    time.sleep(2)
    hits = store.recall(user_id=user_id, query="喜欢喝什么")
    assert len(hits) > 0, f"recall returned no hits: {hits}"


@pytest.mark.skipif(
    not os.getenv("LETTA_URL", "").startswith("http"),
    reason="LETTA_URL not set to real server"
)
def test_letta_store_fallback_when_down():
    from backend.app.memory.service import LettaStore

    store = LettaStore("http://localhost:99999")
    assert not store.available, "Should be unavailable"
    mid = store.write(user_id="u1", content="fallback test")
    assert mid, "fallback write should work"
    hits = store.recall(user_id="u1", query="fallback")
    assert any("fallback" in h.content for h in hits)


@pytest.mark.skipif(
    not os.getenv("LETTA_URL", "").startswith("http"),
    reason="LETTA_URL not set to real server"
)
def test_memory_service_letta_backend():
    import time
    from backend.app.memory.service import MemoryService

    os.environ["MEMORY_BACKEND"] = "letta"
    try:
        svc = MemoryService(
            qdrant_url="memory://test",
            letta_url=os.getenv("LETTA_URL", "http://localhost:8283"),
        )
        assert svc.letta_store is not None
        assert svc.letta_store.available

        user_id = f"test-svc-{int(time.time())}"
        svc.write(user_id=user_id, content="我养了一只猫叫咪咪")

        time.sleep(2)
        hits = svc.recall(user_id=user_id, query="我的猫")
        assert len(hits) > 0, f"recall returned no hits: {hits}"

        assert svc.letta_health() is True
    finally:
        os.environ["MEMORY_BACKEND"] = "memory"
