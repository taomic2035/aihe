# F001 Architecture: His 式超级陪伴 AI — 云为主 · Pi 核心 · Hermes 自进化

> Feature: `F001` | Status: draft | Owner: spark | Date: 2026-08-22  
> Spec: `docs/specs/F001-spec.md` | Research: `docs/research/2026-08-22-synthesis.md`  
> ADR: `docs/decisions/ADR-001-base.md` / `ADR-002-memory.md` / `ADR-003-voice.md`

---

## 1. 架构总览（文字图）

```
┌─────────────────────────────────────────────────────────────────┐
│  Clients (Thin, 云为真相源)                                      │
│  iOS / Android (RN) / Web (Next.js) / PC (Tauri) / WatchOS(SwiftUI)|
│  └─ WebSocket (Realtime) / WebRTC (LiveKit) / Push (APNs/FCM)   │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  API Gateway + Auth (Supabase Auth / OIDC, 限流, 审计)          │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  Agent Gateway — 复用 Hermes Gateway 思想 (单进程, 16+渠道)      │
│  ├─ Session Manager (Postgres + Redis, CRDT 增量同步)           │
│  ├─ Persona Engine (SOUL.md / USER.md / RELATIONSHIP.md + 情感回路)│
│  ├─ Memory Service (Letta + Qdrant + Graphiti)                  │
│  ├─ Voice Pipeline (Pipecat/LiveKit + Deepgram + TTS)           │
│  ├─ Skill Registry (Hermes Skills, agentskills.io)              │
│  ├─ Proactive Scheduler (cron + 情境触发)                        │
│  └─ Safety Layer (AI披露/自伤检测/危机路由/内容过滤)            │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  LLM Router (OpenRouter) → Qwen3 / DeepSeek / GPT-5 / Claude / Hermes3 │
│  Embedding Router → BGE-M3 / Qwen-Embedding                    │
└──────────────────────────┬──────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────────┐
│  Data Plane                                                    │
│  Postgres (主库 + pgvector 兜底) / Qdrant (向量) / Redis (队列/缓存) │
│  Graphiti (时序图谱) / Object Store (S3, 语音/文档)             │
│  Langfuse (trace) / Vector Logs                                │
└─────────────────────────────────────────────────────────────────┘
         ↓ 离线进化
┌─────────────────────────────────────────────────────────────────┐
│  Evolution Plane (离线)                                         │
│  hermes-agent-self-evolution (DSPy+GEPA) + Skill Curator       │
│  评估：synthetic + sessiondb → 门闸 → PR → 人审 → 灰度          │
└─────────────────────────────────────────────────────────────────┘
```

**面向终态检验**：Phase C/D 的产物均在本架构的基座上增量，不存在“脚手架后拆”。

---

## 2. Pi 核心在架构中的落点

### 2.1 Persona Engine
- **文件**：`/persona/SOUL.md`（他的价值观/口吻/边界）、`/persona/USER.md`（用户画像，Honcho 辩证更新）、`/persona/RELATIONSHIP.md`（关系阶段）
- **注入**：每次 LLM 调用前由 Letta 的 Core Memory 管理器分页注入，常驻上下文 ≤4k tokens
- **递归情感回路**（伪代码）：
```python
draft = llm.generate(prompt_with_soul_and_memory)
check = llm.judge("是否温暖、一致、合规？1-5分", draft, soul)
if check.score < 4 and retries < 1:
    draft = llm.rewrite(draft, feedback=check.reason)
tts_params = emotion_to_prosody(check.emotion) # 映射到 ElevenLabs/CosyVoice 情感参数
```

### 2.2 不取的部分
- 不依赖 Pi 私有 API/权重；所有能力通过开箱 LLM + 提示词/轻量 DPO 实现，保留未来 LoRA 人格扩展点

---

## 3. 记忆架构（详见 ADR-002）

- **Letta** 为运行时：Core/Archival/Recall 三层分页，Agent 自主函数调用 `memory_insert / memory_search / memory_edit`
- **Qdrant** 为向量主存：1536维，HNSW，混合 BM25 + 向量，payload 存时间/情感/重要度，TTL 衰减
- **Graphiti** 为图谱：实体（人/地/事件）+ 关系（喜欢/参与/情绪）+ 时序，解决“你上次提到的她是谁”
- **写入**：异步抽取器（LLM 抽取事实→去重归一→写向量+图），失败入死信队列
- **召回**：`embed(query) → Qdrant Top20 → 图遍历扩展 → 重排（时间+重要度+情感相关）→ Top8 注入`
- **审计**：`memory_audit` 表，用户可在客户端“记忆”页查看/删除，删除后向量与图同步删，e2e 测试覆盖

---

## 4. 语音架构（详见 ADR-003）

- **编排**：Pipecat（pipeline 灵活）跑在 LiveKit Transport 上（WebRTC 可靠），两者可互换
- **STT**：Deepgram Nova-3（流式 <300ms）+ Flux EOT 语义端点，VAD 用 Silero
- **TTS**：主 Fish Audio S2 自托管（~100ms TTFB，可克隆），备 ElevenLabs Flash（75ms），中文 CosyVoice 3.0
- **链路**：
```
mic → VAD → Deepgram(stream) → LLM(stream) → TTS(stream) → WebRTC → speaker
              ↕ barge-in（用户打断立即 cancel TTS+LLM）
```
- **成本模型**：级联 $0.04-0.09/min，S2S $0.25-0.35/min；首版默认级联，S2S 仅 Pro 订阅

---

## 5. 云+多端同步

- **真相源**：云 Postgres + Redis；所有客户端 `session_version` 递增，冲突用 LWW + CRDT（Yjs）合并
- **实时**：Supabase Realtime 订阅 `sessions/{user_id}`，增量推送
- **WatchOS**：thin client，功能：推送接收、文本发送、TTS 播放、健康数据上报（心率/睡眠，经 HealthKit→云）；不做 WebRTC 常驻
- **离线**：Redis Stream 队列，端侧重连后 `since_version` 回放；离线占位回复模板

---

## 6. 自进化（Hermes-like）

- **复用**：`NousResearch/hermes-agent-self-evolution` 原样集成
- **流程**：`trace → GEPA 变异 → 评估（synthetic 200条 + sessiondb 100条）→ 门闸（pytest/≤15KB/语义保真）→ PR → 人审 → 灰度 5% → 全量`
- **评估集**：陪伴类需自建（共情、一致性、记忆准确、工具成功、合规），首版 300 条，持续用真实 session 扩充
- **Skills**：存 `skills/{name}/SKILL.md`，版本化，支持 `agentskills.io` 共享

---

## 7. 数据模型（核心表）

```sql
users(id, created_at, region, tier)
sessions(id, user_id, version, created_at)
messages(id, session_id, role, content, modality, tts_params, created_at)
memories(id, user_id, type, content, embedding_id, graph_node_id, importance, created_at, deleted_at)
memory_audit(id, memory_id, action, actor, reason, at)
skills(id, name, version, source, status, eval_score, created_at)
proactive_jobs(id, user_id, cron, trigger, enabled, last_run)
```

---

## 8. 接口契约（节选）

- `POST /v1/chat/completions`（OpenAI 兼容，流式，带 memory 注入）
- `POST /v1/voice/session`（创建 WebRTC 房间，返回 LiveKit token）
- `GET /v1/memories?q=&limit=` / `DELETE /v1/memories/{id}`
- `POST /v1/skills/evolve`（触发 GEPA，返回 PR URL）
- `WS /v1/realtime`（增量消息 + 记忆变更推送）

---

## 9. 部署与可观测

- **一键本地**：`docker compose up`（Gateway + Letta + Qdrant + Postgres + Redis + Langfuse）
- **云**：K8s + Helm，Gateway 多副本 + Redis Sentinel，Qdrant 集群（3节点起）
- **观测**：Langfuse trace（含记忆召回日志）、Prometheus metrics（延迟/召回率/进化 PR 通过率）

---

## 10. 待拍板（OQ）

- OQ-2/3/4 需由 ADR 拍板（见 decisions/）
- OQ-5 WatchOS 首版范围、OQ-6 双部署

> 下一步：请铲屎官评审本架构 + 3 份 ADR，拍板后进入 Phase C 基座实现（TDD + worktree）。
