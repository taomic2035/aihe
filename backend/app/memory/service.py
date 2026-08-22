import os
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
        if not query:
            return [MemoryHit(id=m["id"], content=m["content"], importance=m["importance"]) for m in mems[:limit]]
        q_chars = set(query)
        scored = []
        for m in mems:
            overlap = len(set(m["content"]) & q_chars)
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
    """Real Qdrant implementation with graceful fallback."""

    def __init__(self, url: str):
        self.url = url
        self.fallback = InMemoryStore()
        self.client = None
        self.available = False
        # Try to init real client if library available
        try:
            from qdrant_client import QdrantClient  # type: ignore

            self.client = QdrantClient(url=url, timeout=2)
            # probe
            self.client.get_collections()
            self.available = True
            # ensure collection
            from qdrant_client.models import Distance, VectorParams  # type: ignore

            try:
                self.client.create_collection(
                    collection_name="aihe_memories",
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
                )
            except Exception:
                pass
        except Exception as e:
            # fallback to memory, keep available=False
            self.available = False

    def _embed(self, text: str):
        # placeholder: if real embedding model not configured, use fallback keyword path
        # For now return None to trigger fallback path
        return None

    def write(self, user_id: str, content: str) -> str:
        if not self.available:
            return self.fallback.write(user_id, content)
        try:
            # real path: embed + upsert
            mid = str(uuid.uuid4())
            # embedding mocked as hash for now
            import hashlib

            vec = [float(int(hashlib.md5(content.encode()).hexdigest()[i : i + 2], 16)) / 255 for i in range(0, 32)] * 48  # 1536 dim mock
            self.client.upsert(
                collection_name="aihe_memories",
                points=[{"id": mid, "vector": vec[:1536], "payload": {"user_id": user_id, "content": content}}],
            )
            # also keep fallback for recall without embedding
            self.fallback.write(user_id, content)
            # override id to keep consistent
            self.fallback.store[user_id][-1]["id"] = mid
            return mid
        except Exception:
            return self.fallback.write(user_id, content)

    def recall(self, user_id: str, query: str, limit: int = 8) -> list[MemoryHit]:
        if not self.available:
            return self.fallback.recall(user_id, query, limit)
        try:
            import hashlib

            qvec = [float(int(hashlib.md5(query.encode()).hexdigest()[i : i + 2], 16)) / 255 for i in range(0, 32)] * 48
            res = self.client.query_points(
                collection_name="aihe_memories",
                query=qvec[:1536],
                limit=limit,
                query_filter={"must": [{"key": "user_id", "match": {"value": user_id}}]},
            )
            hits = []
            for p in res.points:
                hits.append(MemoryHit(id=str(p.id), content=p.payload.get("content", ""), importance=0.5))
            if hits:
                return hits
            return self.fallback.recall(user_id, query, limit)
        except Exception:
            return self.fallback.recall(user_id, query, limit)

    def delete(self, user_id: str, memory_id: str):
        self.fallback.delete(user_id, memory_id)
        if self.available:
            try:
                self.client.delete(collection_name="aihe_memories", points_selector=[memory_id])
            except Exception:
                pass


class MemoryService:
    """
    Facade: Letta (Core) + Qdrant (vector) + Postgres (audit) .
    Feature Flag: MEMORY_BACKEND=memory|qdrant|pgvector
    """

    def __init__(self, qdrant_url: str = "memory://test", letta_url: str = "memory://test", db_url: str | None = None):
        backend = os.getenv("MEMORY_BACKEND", "auto")
        # auto: if url is memory:// -> memory, else try qdrant with fallback
        if backend == "memory" or qdrant_url.startswith("memory://"):
            self.store = InMemoryStore()
        elif backend == "qdrant":
            self.store = QdrantStore(qdrant_url)
            # if not available, fallback already handled inside
        else:  # auto
            if qdrant_url.startswith("memory://"):
                self.store = InMemoryStore()
            else:
                # try qdrant, fallback inside
                self.store = QdrantStore(qdrant_url)
        self.letta_url = letta_url
        self.db_url = db_url or os.getenv("DATABASE_URL")

    def write(self, user_id: str, content: str) -> str:
        # TODO: also write to Letta + Postgres audit when available
        # Postgres audit placeholder
        mid = self.store.write(user_id, content)
        # audit log (best effort)
        try:
            if self.db_url and "postgres" in self.db_url:
                pass  # real audit deferred
        except Exception:
            pass
        return mid

    def recall(self, user_id: str, query: str, limit: int = 8) -> list[MemoryHit]:
        return self.store.recall(user_id, query, limit)

    def delete(self, user_id: str, memory_id: str):
        self.store.delete(user_id, memory_id)

    def list(self, user_id: str) -> list[MemoryHit]:
        return self.store.recall(user_id, query="", limit=100)
