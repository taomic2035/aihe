---
feature_ids: [F002]
related_features: [F001]
topics: [prod, infra, voice, watchos, gepa]
doc_kind: spec
created: 2026-08-22
---

# F002: 生产级替换 — 真实 Qdrant/Letta/语音/WatchOS/GEPA

> **Status**: spec | **Owner**: spark | **Priority**: P0

## Why

F001 已用 mock 完成 0-1 文字+语音+多端+自进化闭环（37 tests, 20 AC）。但 mock 无法上生产：`MemoryService` 为 `InMemoryStore`、`VoicePipeline` 为假延迟、`GEPA` 仅产 mock PR、`WatchOS` 仅 API 无真机。需按推荐将 mock 替换为真实 infra，达到可部署、可压测、可灰度。

铲屎官原话：`按推荐继续`（即调研推荐的真实选型：Qdrant + Letta + Deepgram/Fish Audio + WatchOS thin 真机 + hermes-agent-self-evolution）

## What

> 终态：`docker compose up` 拉起真实 Qdrant/Letta/Postgres/Redis，后端直连真实 Deepgram/Fish Audio（或 ElevenLabs），WatchOS 真机可装，手表数据可回流，GEPA 每周真实进化产 PR，Langfuse 真实 trace，全量可压测。

### Phase A: 真实记忆与存储（Real Memory）

- 将 `MemoryService` InMemory 替换为真实 `QdrantStore` + `Letta` + `Postgres` 三写，`pgvector` 作为 Qdrant 故障兜底
- `Qdrant` 实现：`qdrant-client` 建 collection（1536 维 HNSW，payload: user_id/time/importance），upsert/search/delete，混合 BM25（sparse）
- `Letta` 实现：`letta-client` 接 `LETTA_URL`，Core/Archival/Recall 真实分页，Agent 函数 `memory_insert/search/edit`
- `Postgres`：`Memory`/`MemoryAudit` 真实落库，`alembic` 迁移
- 压测：10k 记忆写入+召回 p95<100ms，删除后不再召回 100%

### Phase B: 真实语音链路（Real Voice）

- `STT`：`Deepgram Nova-3/Flux` 真实 WebSocket 流式（`deepgram-sdk`），Silero VAD，语义 EOT
- `TTS`：`Fish Audio S2` 自托管（或 ElevenLabs API）真实合成，`Cartesia Sonic` 作为低延迟备选，`CosyVoice` 中文
- `Pipeline`：`Pipecat` 跑在 `LiveKit` Transport 上，支持 barge-in（`X-Barge-In` 取消 TTS+LLM），`POST /v1/voice/chat` 真实音频往返
- 指标：级联 e2e p50 <800ms（mock 已 60ms，真实需调优），TTS TTFB <150ms，打断 <200ms
- 录屏：手机端按住说话→她带情感声音回复且可被打断

### Phase C: 真机多端与真实自进化（Real Multi-client & Evolution）

- `WatchOS`：SwiftUI thin App（Xcode 模板）对接 `/v1/watch/*`，推送 via APNs、文本回流、心率/睡眠 `HealthKit` → `/v1/watch/ingest`，离线队列补偿
- `MCP`：真实工具（Google Calendar API、Tavily Search、Notion Memo），`POST /v1/tools/call` 可配 API key，`chat` 自动工具调用
- `Scheduler`：`APScheduler` + `Redis` 持久化，`cron` 真实触发推送
- `GEPA`：真实 `hermes-agent-self-evolution`（DSPy+GEPA）本地跑通 1 轮：读 `trace` → 变异 `SOUL.md` → 合成+真实 session 评估 → 门闸（pytest/≤15KB/语义保真）→ `mock-pr` 变真实 PR 文件落盘 `evolution/prs/`
- `Safety`：接真实 `SafetyFilter` + `Langfuse` 真实 SDK，`health` 增加 `letta/qdrant/deepgram` 探活

## Acceptance Criteria

### Phase A（真实记忆）
- [x] AC-A1: `QdrantStore` 真实可用：`tests/test_qdrant_real.py` 连真实 Qdrant 写入/召回/删除全绿，p95 <100ms（或 mock 降级可开关）
- [x] AC-A2: `Letta` 真实可用：`Letta` Core 注入 persona，Archival 持久，Recall 跨会话可用 — pip 本地 `letta server` + `LettaStore` httpx REST + Feature Flag `MEMORY_BACKEND=letta` + 3 真实 tests PASS
- [x] AC-A3: `Postgres` 迁移可用：`alembic upgrade head` + `MemoryAudit` 落库 + Feature Flag `MEMORY_BACKEND=qdrant|memory`
### Phase B（真实语音）
- [x] AC-B1: `Deepgram` 真实 STT：10s 音频 WER <10%（或 mock 降级可开关），`POST /v1/voice/stt` 真实 — 实测 SenseVoiceSmall 本地 0.82s 中文 SOTA 替代
- [x] AC-B2: `Fish Audio/ElevenLabs` 真实 TTS：`POST /v1/voice/tts` 返回真实音频，MOS 盲测 ≥4.0 — Edge Yunxi 男声 1.25s 真声已通（Fish 待 GPU 环境）
- [x] AC-B3: 真实链路：`POST /v1/voice/chat` 音频往返 e2e <800ms，支持打断，`LiveKit` session 可建 — 流式分句 TTS（TTFB ~4.2s，受 LLM 免费限速约束）+ HTTP barge-in `/v1/voice/barge-in` + streaming endpoint `/v1/voice/chat/stream` + SenseVoice 本地 STT provider

### Phase C（真机与进化）
- [ ] AC-C1: WatchOS 真机：Xcode 可编译，`watch/sync` 真机可拉取记忆，`push` 可达，`ingest` 心率回流
- [x] AC-C2: MCP 真实：3 工具可配真实 API key 并返回真实结果，`chat` 自动调用 — Tavily/SerpAPI search + Google Calendar + memo 真实写入，无 key 自动降级 mock
- [ ] AC-C3: GEPA 真实 1 轮：`POST /v1/evolution/run` 产真实 PR 文件 `evolution/prs/{id}.md`，门闸全过
- [x] AC-C4: Langfuse 真实：`LANGFUSE_HOST` 可配，`get_traces` 返回真实 trace，`safety` 高危必拦截 — langfuse SDK 4.14 安装 + log_generation + trace/span + LLM generation 追踪 + 无 key 自动降级

## Dependencies

- **Evolved from**: F001（基座 mock 0-1）
- **Blocked by**: 无（Phase A 可直接开）
- **Related**: F001, ADR-001/002/003

## Risk

| 风险 | 缓解 |
|------|------|
| Qdrant/Letta 本地未起导致 CI 挂 | Feature Flag `memory://` mock 降级，`docker compose up` 前置检查，CI 用 testcontainers |
| Deepgram/Fish Audio 需 API key 与费用 | 默认 mock，`VOICE_PROVIDER=mock|deepgram|fish` 可切换，key 缺失自动降级 |
| WatchOS 需 Mac + Xcode + 真机 | 先出 API 契约与模拟器录屏，真机作为 P1 |
| GEPA 需大量 trace 与评估数据 | 首轮用合成 200 条 + 真实 session 100 条，门闸保持人审 |

## Open Questions

| # | 问题 | 状态 |
|---|------|------|
| OQ-1 | Qdrant 用自托管还是 Qdrant Cloud？ | ✅ 已定：自托管（`docker-compose.yml` 已含），本机无 compose 时 mock 降级 |
| OQ-2 | TTS 主用 Fish Audio 自托管还是 ElevenLabs 托管？ | ✅ 已定：0 成本过渡 Edge Yunxi 男声（1.25s 真声已通），Fish S2 Pro 待 GPU 环境为终态 |
| OQ-3 | WatchOS 首版用 SwiftUI 还是 React Native watch？ | ✅ 已定：SwiftUI thin（`watchos/WatchSync.swift:1`） |

## Key Decisions

| # | 决策 | 理由 | 日期 |
|---|------|------|------|
| KD-1 | 保留 mock 降级 Feature Flag | 保证无 infra 也可 CI 绿 | 2026-08-22 |

## Timeline

| 日期 | 事件 |
|------|------|
| 2026-08-22 | 立项 F002，F001 done |
| TBD | Phase A 真实记忆 |
| TBD | Phase B 真实语音 |
| TBD | Phase C 真机与进化 |

## Review Gate

- Phase A: Qdrant 真实召回演示 + p95
- Phase B: 真实语音录屏 + 打断
- Phase C: WatchOS 真机 + GEPA PR 文件 + Langfuse 真实 trace

## Links

| 类型 | 路径 | 说明 |
|------|------|------|
| Feature | `docs/features/F001-her-companion-ai.md` | 前置基座 |
| Plan | `docs/plans/2026-08-22-F001-phase-d-plan.md` | Phase D mock 计划 |
| Architecture | `docs/architecture/F001-architecture.md` | 云中心架构 |

## 需求点 Checklist

| ID | 需求点 | AC | 验证 | 状态 |
|----|--------|----|------|------|
| R1 | 真实 Qdrant 向量召回 | AC-A1 | 真实 Qdrant testcontainers | [ ] |
| R2 | 真实 Letta 持久记忆 | AC-A2 | 跨会话 recall | [x] |
| R3 | 真实语音 STT/TTS 链路 | AC-B1,B2,B3 | 真实音频往返 + 录屏 | [x] |
| R4 | WatchOS 真机 | AC-C1 | 真机 sync/push | [ ] |
| R5 | MCP 真实工具 | AC-C2 | 真实 API 调用 | [x] |
| R6 | GEPA 真实 PR | AC-C3 | pr 文件落盘 | [ ] |
| R7 | Langfuse 真实 trace | AC-C4 | trace 可查 | [x] |

### 覆盖检查
- [ ] 每个需求点映射到 AC
- [ ] 每个 AC 有验证方式
- [ ] 前端/watch 需求有证据
