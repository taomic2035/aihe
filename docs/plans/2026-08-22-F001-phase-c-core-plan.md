# F001 Phase C Core Platform Implementation Plan

**Feature:** F001 — `docs/features/F001-her-companion-ai.md`
**Goal:** 实现云为主的可运行基座，文字陪伴闭环先跑通（Gateway+Letta+Qdrant+Persona+Chat+记忆审计），为 Phase D 语音/多端/自进化打地基
**Acceptance Criteria:**
- AC-C1: `docker compose up` 一键拉起 Gateway + Letta + Qdrant + Postgres + Redis，健康检查全绿
- AC-C2: 文字陪伴闭环可演示：Web 端与手机端同一用户对话，记忆跨端一致，支持流式、人格一致、记忆召回（单元+集成测试覆盖）
- AC-C3: 记忆审计面板可用：用户可查看/删除单条记忆，验证删除后不再被召回
- AC-C4: 基础观测：Langfuse 全链路 trace + 记忆检索日志可查
**Architecture:** 复用 Hermes Gateway 思想自研轻量 Gateway（Node/Python），Letta 为记忆 runtime，Qdrant 为向量主存，Postgres 为主库，Redis 为队列/缓存，OpenRouter 为 LLM 路由，Pi 核心以 SOUL.md + 情感回路实现
**Tech Stack:** Python 3.12/FastAPI, Node 20 (Gateway), Letta 0.4+, Qdrant 1.11, Postgres 16 + pgvector, Redis 7, OpenRouter API, Docker Compose, Next.js 14 (Web), React Native (壳), Langfuse
**前端验证:** Yes — Web 记忆审计面板 + 跨端同步需 Playwright 真机验证

---

## Straight-Line Check

**Finish line (B):** 用户在 Web 与手机用同一账号对话，云上同一“她”响应（SOUL 一致），记忆跨端可见且可删，`docker compose up` 即得全栈
**Terminal schema:**
```python
# persona/
SOUL.md: str # 价值观/口吻/边界
USER.md: str # 画像，Honcho 更新
RELATIONSHIP.md: str

# memory
Memory(id, user_id, type, content, embedding, graph_node_id, importance, created_at, deleted_at)
MemoryAudit(id, memory_id, action, actor, at)

# chat
Message(id, session_id, user_id, role, content, created_at)
Session(id, user_id, version, created_at)

# api
POST /v1/chat/completions -> streaming SSE
GET /v1/memories -> list
DELETE /v1/memories/{id}
GET /health, /v1/realtime WS
```
**Not building:** 语音（Phase D）、WatchOS、手写 GEPA（仅预留接口）

---

## Task 1: 项目脚手架与 Docker Compose

**Files:**
- Create: `docker-compose.yml`
- Create: `backend/pyproject.toml`
- Create: `backend/app/main.py`
- Create: `gateway/package.json`
- Create: `.env.example`

**Step 1: Write failing test**

```python
# tests/test_compose.py
def test_compose_has_required_services():
    import yaml
    data = yaml.safe_load(open("docker-compose.yml"))
    for svc in ["postgres","redis","qdrant","letta","backend","gateway"]:
        assert svc in data["services"]
```

**Step 2: Run test to verify it fails**

Run: `pytest tests/test_compose.py -v`
Expected: FAIL "No such file"

**Step 3: Write minimal implementation**

- `docker-compose.yml` 定义 6 服务（postgres:16, redis:7, qdrant, letta, backend:8000, gateway:3000），backend 依赖 postgres/redis/qdrant/letta
- `backend/app/main.py` FastAPI with `/health` -> {"status":"ok", "services":{"postgres":...}}
- `.env.example` 含 OPENROUTER_API_KEY, QDRANT_URL, LETTA_URL

**Step 4: Run test to verify it passes**

Run: `pytest tests/test_compose.py -v` → PASS; `docker compose config` 验证

**Step 5: Commit**

```bash
git add docker-compose.yml backend/ gateway/ .env.example tests/test_compose.py
git commit -m "feat(F001-C): scaffold docker compose + health [spark/Muse-Spark-1.2🐾]"
```

---

## Task 2: 数据模型与迁移

**Files:**
- Create: `backend/app/models.py`
- Create: `backend/alembic/versions/001_init.py`
- Test: `tests/test_models.py`

**Step 1: Write failing test**

```python
def test_create_memory_and_audit():
    # 需能创建 memory，删除后 audit 有记录且查询不再返回
```

**Step 2: Run fails**

**Step 3: Implement**

- SQLAlchemy models: User, Session, Message, Memory, MemoryAudit
- Memory: id UUID, user_id FK, type enum(episodic/semantic), content text, embedding_id, graph_node_id, importance float, deleted_at nullable
- Alembic migration 001

**Step 4: Run pass** `pytest tests/test_models.py -v`

**Step 5: Commit**

---

## Task 3: Persona Engine（Pi 核心）

**Files:**
- Create: `persona/SOUL.md`
- Create: `persona/USER.md`
- Create: `persona/RELATIONSHIP.md`
- Create: `backend/app/persona/service.py`
- Test: `tests/test_persona.py`

**Step 1: Failing test**

```python
def test_persona_injection():
    svc = PersonaService()
    prompt = svc.build_system_prompt(user_id="u1")
    assert "SOUL" in prompt and "USER" in prompt
```

**Step 2: Fail**

**Step 3: Implement**

- SOUL.md 初版（温暖、主动、非命令式、Her 式口吻，含边界：明确 AI 身份）
- USER.md 模板 + Honcho 风格更新接口 `update_user_profile(user_id, facts)`
- `build_system_prompt()` 拼接三件套 + Letta Core Memory
- 递归情感回路 `empathy_check(draft)` 轻量 LLM judge（≤1 重试）

**Step 4: Pass**

**Step 5: Commit**

---

## Task 4: Memory Service（Letta + Qdrant）

**Files:**
- Create: `backend/app/memory/letta_client.py`
- Create: `backend/app/memory/qdrant_client.py`
- Create: `backend/app/memory/service.py`
- Test: `tests/test_memory_service.py`

**Step 1: Failing test**

```python
def test_memory_write_and_recall():
    svc = MemoryService()
    svc.write(user_id="u1", content="我喜欢喝美式，住在上海")
    hits = svc.recall(user_id="u1", query="我喜欢喝什么")
    assert any("美式" in h.content for h in hits)
```

**Step 2: Fail**

**Step 3: Implement**

- `letta_client`: 封装 Letta API（Core/Archival/Recall），分页管理
- `qdrant_client`: upsert/search，payload 含 user_id/time/importance，混合 BM25（Qdrant 1.11 sparse）
- `service.write`: 抽取→去重→双写（Qdrant+Letta+Postgres）
- `service.recall`: embed→Qdrant Top20→重排→Top8
- `service.delete`: 软删 + 向量/图同步删 + audit

**Step 4: Pass (需 mock Qdrant/Letta 或用 testcontainers)**

**Step 5: Commit**

---

## Task 5: LLM Router（OpenRouter）

**Files:**
- Create: `backend/app/llm/router.py`
- Test: `tests/test_llm_router.py`

**Step 1: Failing test** `test_router_streams_with_persona_and_memory()`

**Step 2: Fail**

**Step 3: Implement**

- OpenRouter 兼容 OpenAI SDK，模型映射：`qwen3:qwen/qwen3-32b`, `deepseek:deepseek/deepseek-chat`, 可切 `openai/gpt-5`, `anthropic/claude-4`
- 流式 SSE，注入 persona + 召回记忆
- 重试与 fallback

**Step 4: Pass**

**Step 5: Commit**

---

## Task 6: Chat API（流式）

**Files:**
- Create: `backend/app/api/chat.py`
- Modify: `backend/app/main.py: add router`
- Test: `tests/test_chat_api.py`

**Step 1: Failing test**

```python
def test_chat_stream(client):
    r = client.post("/v1/chat/completions", json={"user_id":"u1","message":"你好"})
    assert r.status_code == 200 and "data:" in r.text
```

**Step 2: Fail**

**Step 3: Implement**

- `POST /v1/chat/completions`：1) recall memory 2) build prompt 3) llm.stream 4) async write memory（后台）
- SSE 格式，支持 persona 情感校验重试
- Session version 递增

**Step 4: Pass**

**Step 5: Commit**

---

## Task 7: Memory Audit 面板（Backend+Web）

**Files:**
- Create: `backend/app/api/memories.py` (GET/DELETE)
- Create: `web/app/memories/page.tsx`
- Test: `tests/test_memories_api.py`

**Step 1: Failing test** `test_delete_memory_not_recalled()`

**Step 2: Fail**

**Step 3: Implement**

- `GET /v1/memories?user_id=&q=&limit=` → Qdrant+PG 联查
- `DELETE /v1/memories/{id}` → 软删+Qdrant删
- Web: Next.js 列表页，显示 content/time/importance，按钮删除，调用 API

**Step 4: Pass + Playwright 截图**

**Step 5: Commit**

---

## Task 8: 多端同步（Realtime）

**Files:**
- Create: `backend/app/realtime/manager.py`
- Modify: `backend/app/api/chat.py` (broadcast)
- Create: `web/hooks/useRealtime.ts`
- Test: `tests/test_realtime.py`

**Step 1: Failing test** `test_two_clients_same_memory()`

**Step 2: Fail**

**Step 3: Implement**

- WS `/v1/realtime?user_id=`，Redis Pub/Sub 广播新 message/memory 事件
- Web 端订阅，收到增量更新会话
- 版本控制 LWW

**Step 4: Pass**

**Step 5: Commit**

---

## Task 9: 可观测（Langfuse）

**Files:**
- Modify: `backend/app/llm/router.py` (wrap)
- Create: `backend/app/observability/langfuse.py`
- Test: `tests/test_observability.py`

**Step 1: Failing test** `test_trace_contains_memory_recall()`

**Step 2: Fail**

**Step 3: Implement**

- Langfuse SDK 装饰 llm 调用与 memory recall，记录 prompt/mems/latency
- `GET /health` 增加 trace 健康

**Step 4: Pass**

**Step 5: Commit**

---

## Task 10: 端到端集成与演示

**Files:**
- Create: `tests/e2e/test_cross_client.py`
- Create: `scripts/demo.sh`

**Step 1: Failing test**

```python
def test_cross_client_flow():
    # client A 发消息 -> client B 通过 WS 收到 -> B 问记忆 -> 召回 A 的信息
```

**Step 2: Fail**

**Step 3: Implement**

- 脚本 `demo.sh`: docker compose up + 种子用户 + 演示对话
- 补齐缺口

**Step 4: Pass** `pytest tests/e2e -v` + 手动跨端演示录屏

**Step 5: Commit** + 更新 `docs/features/F001-her-companion-ai.md` AC-C1~4 打勾

---

## 验证清单

- [ ] `docker compose up -d && curl /health` 全绿
- [ ] `pytest -q` 全绿
- [ ] Web 记忆面板截图 + 跨端同步录屏（≤15s）
- [ ] `GET /v1/memories` 删除后不再召回 e2e
- [ ] Langfuse trace 可查

## 下一步

计划落盘后 → 加载 `worktree` 技能 → 创建隔离开发环境 → `tdd` 开始 Task 1
