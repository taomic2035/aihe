def test_memory_write_and_recall():
    from backend.app.memory.service import MemoryService

    svc = MemoryService(qdrant_url="memory://test", letta_url="memory://test")
    svc.write(user_id="u1", content="我喜欢喝美式，住在上海")
    svc.write(user_id="u1", content="我养了一只猫叫咪咪")
    hits = svc.recall(user_id="u1", query="我喜欢喝什么")
    assert any("美式" in h.content for h in hits), f"hits={hits}"

    hits2 = svc.recall(user_id="u1", query="我的猫叫什么")
    assert any("咪咪" in h.content for h in hits2)


def test_memory_delete_not_recalled():
    from backend.app.memory.service import MemoryService

    svc = MemoryService(qdrant_url="memory://test", letta_url="memory://test")
    mid = svc.write(user_id="u1", content="我明天要去北京")
    hits = svc.recall(user_id="u1", query="去哪里")
    assert any("北京" in h.content for h in hits)
    svc.delete(user_id="u1", memory_id=mid)
    hits2 = svc.recall(user_id="u1", query="去哪里")
    assert all("北京" not in h.content for h in hits2)


def test_memory_user_isolation():
    from backend.app.memory.service import MemoryService

    svc = MemoryService(qdrant_url="memory://test", letta_url="memory://test")
    svc.write(user_id="u1", content="u1 的秘密")
    svc.write(user_id="u2", content="u2 的秘密")
    hits = svc.recall(user_id="u1", query="秘密")
    assert all("u2" not in h.content for h in hits)
