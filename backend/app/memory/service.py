import uuid
from dataclasses import dataclass


@dataclass
class MemoryHit:
    id: str
    content: str
    importance: float = 0.5


class InMemoryStore:
    """Fallback when qdrant_url == memory:// — for tests and local dev without infra."""

    def __init__(self):
        self.store: dict[str, list[dict]] = {}  # user_id -> list[mem]

    def write(self, user_id: str, content: str) -> str:
        mid = str(uuid.uuid4())
        self.store.setdefault(user_id, []).append(
            {"id": mid, "content": content, "deleted": False, "importance": 0.5}
        )
        return mid

    def recall(self, user_id: str, query: str, limit: int = 8) -> list[MemoryHit]:
        mems = [m for m in self.store.get(user_id, []) if not m["deleted"]]
        # naive keyword overlap score
        q_chars = set(query)
        scored = []
        for m in mems:
            overlap = len(set(m["content"]) & q_chars)
            # also boost if query substring in content
            if any(kw in m["content"] for kw in query.split(" ")):
                overlap += 5
            scored.append((overlap, m))
        scored.sort(key=lambda x: x[0], reverse=True)
        hits = []
        for score, m in scored:
            if score > 0:
                hits.append(MemoryHit(id=m["id"], content=m["content"], importance=m["importance"]))
        return hits[:limit]

    def delete(self, user_id: str, memory_id: str):
        for m in self.store.get(user_id, []):
            if m["id"] == memory_id:
                m["deleted"] = True
                break


class QdrantStore:
    """Real Qdrant implementation — deferred until infra available."""

    def __init__(self, url: str):
        self.url = url
        # TODO: init qdrant_client.QdrantClient

    def write(self, user_id: str, content: str) -> str:
        raise NotImplementedError("QdrantStore not yet implemented, use memory:// for dev")

    def recall(self, user_id: str, query: str, limit: int = 8) -> list[MemoryHit]:
        raise NotImplementedError

    def delete(self, user_id: str, memory_id: str):
        raise NotImplementedError


class MemoryService:
    """
    Facade: Letta (Core) + Qdrant (vector) + Postgres (audit) .
    TDD phase uses InMemoryStore when qdrant_url == memory://
    """

    def __init__(self, qdrant_url: str = "memory://test", letta_url: str = "memory://test", db_url: str | None = None):
        if qdrant_url.startswith("memory://"):
            self.store = InMemoryStore()
        else:
            self.store = QdrantStore(qdrant_url)
        self.letta_url = letta_url

    def write(self, user_id: str, content: str) -> str:
        # TODO: also write to Letta + Postgres audit
        return self.store.write(user_id, content)

    def recall(self, user_id: str, query: str, limit: int = 8) -> list[MemoryHit]:
        return self.store.recall(user_id, query, limit)

    def delete(self, user_id: str, memory_id: str):
        self.store.delete(user_id, memory_id)

    def list(self, user_id: str) -> list[MemoryHit]:
        return self.store.recall(user_id, query="", limit=100)
