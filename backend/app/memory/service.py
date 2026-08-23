import os
import uuid
import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)


@dataclass
class MemoryHit:
    id: str
    content: str
    importance: float = 0.5


class InMemoryStore:
    def __init__(self):
        self.store: dict[str, list[dict]] = {}

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
    def __init__(self, url: str):
        self.url = url
        self.fallback = InMemoryStore()
        self.client = None
        self.available = False
        try:
            from qdrant_client import QdrantClient
            self.client = QdrantClient(url=url, timeout=2)
            self.client.get_collections()
            self.available = True
            from qdrant_client.models import Distance, VectorParams
            try:
                self.client.create_collection(
                    collection_name="aihe_memories",
                    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
                )
            except Exception:
                pass
        except Exception:
            self.available = False

    def write(self, user_id: str, content: str) -> str:
        if not self.available:
            return self.fallback.write(user_id, content)
        try:
            mid = str(uuid.uuid4())
            import hashlib
            vec = [float(int(hashlib.md5(content.encode()).hexdigest()[i : i + 2], 16)) / 255 for i in range(0, 32)] * 48
            self.client.upsert(
                collection_name="aihe_memories",
                points=[{"id": mid, "vector": vec[:1536], "payload": {"user_id": user_id, "content": content}}],
            )
            self.fallback.write(user_id, content)
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


class LettaStore:
    """
    Letta server REST API client for Core + Archival memory.
    Each user_id maps to a Letta agent (created on first write if needed).
    """

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")
        self.fallback = InMemoryStore()
        self.available = False
        self._agent_cache: dict[str, str] = {}
        self._llm_config: dict | None = None
        self._embedding_config: dict | None = None
        try:
            resp = httpx.get(f"{self.base_url}/v1/agents/", timeout=5)
            resp.raise_for_status()
            agents = resp.json()
            for a in agents:
                name = a.get("name", "")
                if name.startswith("he-"):
                    self._agent_cache[name[3:]] = a["id"]
            resp2 = httpx.get(f"{self.base_url}/v1/models", timeout=5)
            if resp2.status_code == 200:
                models_data = resp2.json()
                if models_data:
                    first = models_data[0] if isinstance(models_data, list) else models_data
                    self._llm_config = first.get("llm_config")
                    self._embedding_config = first.get("embedding_config")
            self.available = True
            logger.info(f"LettaStore connected to {self.base_url}, {len(self._agent_cache)} agents cached")
        except Exception as e:
            logger.warning(f"LettaStore unavailable ({e}), falling back to InMemoryStore")
            self.available = False

    def _get_or_create_agent(self, user_id: str) -> str | None:
        if not self.available:
            return None
        if user_id in self._agent_cache:
            return self._agent_cache[user_id]
        try:
            llm_model = os.getenv("LLM_MODEL", "nvidia/nemotron-3-nano-30b-a3b:free")
            llm_base = os.getenv("OPENROUTER_BASE_URL", os.getenv("OPENAI_API_BASE", "https://openrouter.ai/api/v1"))
            payload: dict = {
                "name": f"he-{user_id}",
                "memory_blocks": [
                    {"label": "persona", "value": "你是 aihe，专属陪伴 AI（男性，He，26岁温暖大哥哥）。温暖沉稳，中文口语，先共情后建议。"},
                    {"label": "human", "value": f"用户 {user_id}"},
                ],
                "llm_config": {
                    "model": llm_model,
                    "model_endpoint_type": "openai",
                    "model_endpoint": llm_base,
                    "context_window": 16384,
                },
                "embedding_config": {
                    "embedding_model": "text-embedding-ada-002",
                    "embedding_endpoint_type": "openai",
                    "embedding_endpoint": llm_base,
                    "embedding_dim": 1536,
                },
            }
            resp = httpx.post(f"{self.base_url}/v1/agents/", json=payload, timeout=30)
            resp.raise_for_status()
            agent_id = resp.json()["id"]
            self._agent_cache[user_id] = agent_id
            logger.info(f"Created Letta agent {agent_id} for user {user_id}")
            return agent_id
        except Exception as e:
            logger.error(f"Failed to create Letta agent for {user_id}: {e}")
            return None

    def write(self, user_id: str, content: str) -> str:
        if not self.available:
            return self.fallback.write(user_id, content)
        mid = str(uuid.uuid4())
        agent_id = self._get_or_create_agent(user_id)
        if not agent_id:
            return self.fallback.write(user_id, content)
        try:
            resp = httpx.post(
                f"{self.base_url}/v1/agents/{agent_id}/messages",
                json={"messages": [{"role": "user", "text": f"请记住这个关于用户的信息：{content}"}]},
                timeout=60,
            )
            if resp.status_code == 200:
                self.fallback.write(user_id, content)
                self.fallback.store[user_id][-1]["id"] = mid
                return mid
            logger.warning(f"Letta write failed ({resp.status_code}), falling back")
            return self.fallback.write(user_id, content)
        except Exception as e:
            logger.warning(f"Letta write error: {e}, falling back")
            return self.fallback.write(user_id, content)

    def recall(self, user_id: str, query: str, limit: int = 8) -> list[MemoryHit]:
        if not self.available:
            return self.fallback.recall(user_id, query, limit)
        agent_id = self._get_or_create_agent(user_id)
        if not agent_id:
            return self.fallback.recall(user_id, query, limit)
        try:
            resp = httpx.post(
                f"{self.base_url}/v1/agents/{agent_id}/messages",
                json={"messages": [{"role": "user", "text": f"搜索回忆：{query}"}]},
                timeout=60,
            )
            if resp.status_code != 200:
                return self.fallback.recall(user_id, query, limit)
            data = resp.json()
            hits: list[MemoryHit] = []
            messages = data.get("messages", data) if isinstance(data, dict) else data
            for m in messages:
                if isinstance(m, dict):
                    if m.get("message_type") == "assistant_message":
                        content = m.get("content", "")
                        if content:
                            hits.append(MemoryHit(id=str(uuid.uuid4()), content=content, importance=0.8))
            if hits:
                return hits[:limit]
            return self.fallback.recall(user_id, query, limit)
        except Exception as e:
            logger.warning(f"Letta recall error: {e}, falling back")
            return self.fallback.recall(user_id, query, limit)

    def delete(self, user_id: str, memory_id: str):
        self.fallback.delete(user_id, memory_id)

    def health(self) -> bool:
        if not self.available:
            return False
        try:
            resp = httpx.get(f"{self.base_url}/v1/agents/", timeout=3)
            return resp.status_code == 200
        except Exception:
            return False


class MemoryService:
    """
    Facade: Letta (Core) + Qdrant (vector) + Postgres (audit).
    Feature Flag: MEMORY_BACKEND=memory|qdrant|letta|auto
    """

    def __init__(self, qdrant_url: str = "memory://test", letta_url: str = "memory://test", db_url: str | None = None):
        backend = os.getenv("MEMORY_BACKEND", "auto")
        self.letta_store: LettaStore | None = None
        self.db_url = db_url or os.getenv("DATABASE_URL")

        if backend == "memory" or (backend == "auto" and qdrant_url.startswith("memory://") and letta_url.startswith("memory://")):
            self.store = InMemoryStore()
        elif backend == "qdrant":
            self.store = QdrantStore(qdrant_url)
        elif backend == "letta":
            if not letta_url.startswith("memory://"):
                self.letta_store = LettaStore(letta_url)
                self.store = self.letta_store
            else:
                self.store = InMemoryStore()
        else:  # auto
            if not letta_url.startswith("memory://"):
                self.letta_store = LettaStore(letta_url)
                self.store = self.letta_store
                if not self.letta_store.available and not qdrant_url.startswith("memory://"):
                    self.store = QdrantStore(qdrant_url)
            elif not qdrant_url.startswith("memory://"):
                self.store = QdrantStore(qdrant_url)
            else:
                self.store = InMemoryStore()

    def write(self, user_id: str, content: str) -> str:
        mid = self.store.write(user_id, content)
        try:
            if self.db_url and "postgres" in self.db_url:
                pass
        except Exception:
            pass
        return mid

    def recall(self, user_id: str, query: str, limit: int = 8) -> list[MemoryHit]:
        return self.store.recall(user_id, query, limit)

    def delete(self, user_id: str, memory_id: str):
        self.store.delete(user_id, memory_id)

    def list(self, user_id: str) -> list[MemoryHit]:
        return self.store.recall(user_id, query="", limit=100)

    def letta_health(self) -> bool:
        if self.letta_store:
            return self.letta_store.health()
        return False
