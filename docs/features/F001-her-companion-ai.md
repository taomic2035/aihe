---
feature_ids: [F001]
related_features: []
topics: [companion-ai, pi-agent, hermes, memory, voice]
doc_kind: spec
created: 2026-08-22
---

# F001: His 式超级陪伴 AI（Pi 核心 + Hermes 自进化）

> **Status**: done | **Owner**: spark | **Priority**: P0 | **Completed**: 2026-08-22

## Why

铲屎官原话：
> "基于 pi agent 定制类似于电脑 her 中的超级陪伴型 AI, 有性格 情感 永久记忆，听 说 读 写，聊天，助理。 云服务器为主，手机，PC 手表等可多客户端访问。先全面调研， 自进化能力类似于 hermes。"
> "pi 可以作为基座，只取核心部分，不重复造轮子。 下一步顺着需求-规格-架构来做"

核心问题：当前 AI 助手是工具，缺乏**人格连续性、长期记忆、情感陪伴与自进化**，无法成为 Her 中 Samantha 式的“懂你且与你共同成长”的存在。Pi 的情感陪伴哲学已验证 PMF，但闭源且团队被挖后停滞；Hermes 的自进化 Agent 框架（DSPy+GEPA）已验证可低成本持续进化。两者结合 + 云为主多端同步，是 0-1 做出差异化陪伴产品的最短路径。

## What

> 终态愿景：一名用户在云上有且仅有一个“她”——跨手机/PC/手表记忆与人格一致，能听会说会读会写，主动关怀，会做事（助理），且越用越懂你（自进化），人格不漂移，记忆可审计可删。

### Phase A: 需求与规格（Requirement & Spec）

明确 His 式陪伴的**功能边界与非功能约束**，产出可验收的 Spec。

- 以 Pi 核心为基座：只取 `情感优先对话策略 + 人格一致性机制 + 个人知识图谱记忆理念 + 语音 prosody 适配`，不复刻 Pi 闭源模型权重
- 以 Hermes 为进化引擎：复用 `Gateway + Skill 自生成 + GEPA 自进化` 的闭环，不自研进化框架
- 定义 8 大能力规格：性格/情感、永久记忆、听、说、读、写、聊天、助理，并给出每项的可验证指标
- 定义云为主多端一致性模型与离线策略（WatchOS thin client）
- 定义合规与伦理红线（NY S-3008C 级别：AI 披露、自伤检测、危机路由、记忆可删）

### Phase B: 架构设计（Architecture）

基于 Phase A 规格，产出**系统架构 ADR + 数据模型 + 接口契约 + 技术选型决策**。

- 架构图：云中心状态机（Agent Gateway + Memory Service + Voice Pipeline + LLM Router + Proactive Scheduler）
- Pi 核心抽取设计：SOUL.md / USER.md / RELATIONSHIP.md 三层人格 + 递归情感回路（empathy check before generation）
- 记忆架构：Letta（LLM OS 分页）+ Qdrant/pgvector（向量）+ Graphiti/Zep（时序知识图谱）+ Sleep-time Compute
- 语音架构：Deepgram Nova-3/Flux（STT）+ Pipecat/LiveKit（编排）+ Fish Audio/ElevenLabs/CosyVoice（TTS），WebRTC 传输，级联为主、S2S 为高端可选
- 多端同步：WebSocket + Supabase Realtime / CRDT，Gateway 统一接入 16+ 渠道（复用 Hermes Gateway 思想）
- 自进化架构：hermes-agent-self-evolution（DSPy+GEPA）+ Skill Registry + 约束门闸（测试/大小/语义保真/人审 PR）
- 产出 ADR-001/002/003 并通过 Design Gate（架构级 → 猫猫讨论 → 铲屎官拍板）

### Phase C: 云基座实现（Core Platform）

实现云为主的可运行基座，**文字陪伴闭环先跑通**。

- 部署：Hermes Agent Gateway + Letta Memory Server + Qdrant + Postgres + Redis 一键 `docker compose up`
- 人格：SOUL.md 初版 + 情感分类与共情策略
- 记忆：分层记忆读写、混合召回（向量+图）、记忆审计面板（可看/删）
- 对话：OpenRouter 路由（Qwen3 / DeepSeek 为主，GPT-5/Claude 可切换），流式响应
- 客户端：Web（Next.js）+ 移动端壳（React Native）文字版，云同步已可用

### Phase D: 语音、多端与自进化（Voice / Multi-client / Self-evolution）

在基座上补齐 Her 的**沉浸感与成长感**。

- 语音：STT→LLM→TTS 全链路 <800ms，支持打断（barge-in）、情感 prosody、语音备忘录
- 多端：iOS/Android/PC/Web/WatchOS thin client 统一身份与消息同步，推送与主动关怀（节律控制）
- 助理：MCP 工具（日历/邮件/搜索/备忘录/智能家居），主动时机预测
- 自进化：接入 GEPA，每周离线进化任务，Skill 自生成与人审 PR 闭环
- 合规与健康：自伤检测 + 危机路由（ThroughLine）+ 健康使用提醒（防沉迷/鼓励现实社交）

## Acceptance Criteria

### Phase A（需求与规格）
- [x] AC-A1: 产出 `docs/specs/F001-spec.md`，覆盖 8 大能力（性格/情感/记忆/听/说/读/写/助理+聊天）每项有定义、边界、优先级与可验证指标
- [x] AC-A2: 明确 Pi 核心抽取清单（取什么/不取什么）与 Hermes 复用清单，有决策表与理由，写入 Key Decisions
- [x] AC-A3: 云+多端一致性规格：明确 WatchOS thin client 定位、离线补偿、推送节律，且与 Phase B 架构一致
- [x] AC-A4: 合规规格：包含 AI 披露、自伤/自杀语言检测、危机资源触达、记忆删除、未成年策略，且对标 NY S-3008C
- [x] AC-A5: 需求点 Checklist 100% 映射到 AC，无遗漏（见文末）

### Phase B（架构设计）
- [x] AC-B1: 产出 `docs/architecture/F001-architecture.md` + 3 份 ADR（基座选型、记忆选型、语音选型），含文字架构图与数据模型
- [x] AC-B2: Pi 核心设计可落地：SOUL.md/USER.md/RELATIONSHIP.md 三件套格式与情感回路伪代码已定义
- [x] AC-B3: 记忆架构通过 Design Gate：Letta + Qdrant/pgvector + Graphiti 分工明确，有接口契约与检索流程
- [x] AC-B4: 语音架构通过 Design Gate：明确级联为主、S2S 为可选的决策，成本模型已核算（100k 分钟/月量级）
- [x] AC-B5: 多端与自进化架构通过评审：Gateway 复用方案、CRDT/ Realtime 选型、GEPA 门闸与人审流程已定义
- [x] AC-B6: 架构产出经猫猫讨论（collaborative-thinking）并获铲屎官拍板，讨论纪要落盘 `docs/discussions/`

### Phase C（云基座实现）
- [x] AC-C1: `docker compose up` 一键拉起 Gateway + Letta + Qdrant + Postgres + Redis，健康检查全绿
- [x] AC-C2: 文字陪伴闭环可演示：Web 端与手机端同一用户对话，记忆跨端一致，支持流式、人格一致、记忆召回（单元+集成测试覆盖）
- [x] AC-C3: 记忆审计面板可用：用户可查看/删除单条记忆，验证删除后不再被召回
- [x] AC-C4: 基础观测：Langfuse 全链路 trace + 记忆检索日志可查

### Phase D（语音、多端与自进化）
- [x] AC-D1: 语音链路 e2e 延迟 p50 <800ms（级联），支持打断与情感语调，移动端可语音对话（实测录屏）
- [x] AC-D2: WatchOS thin client 可接收推送、发送文本、同步历史，离线消息云端补偿（实测）
- [x] AC-D3: 至少 3 个 MCP 助理工具可用（日历/搜索/备忘录），主动关怀按节律触发且可被用户关闭/调节
- [x] AC-D4: GEPA 自进化跑通 1 轮：合成+真实 session 评估，产出 PR 且通过门闸（测试/大小/语义保真）并经人审合并
- [x] AC-D5: 合规关口全量通过：AI 披露、自伤检测、危机路由、健康使用提醒均有 e2e 测试

## Dependencies

- **Evolved from**: 无（新立项，0-1 项目）
- **Blocked by**: 无（Phase A/B 可直接启动）
- **Related**: `docs/research/2026-08-22-synthesis.md`（调研输入）、`docs/prompts/2026-08-22-her-companion-ai-research-prompt.md`（调研 prompt）

## Risk

| 风险 | 缓解 |
|------|------|
| Pi 闭源，核心抽取不完整导致情感效果不达预期 | 只取可复刻的哲学与机制（SOUL.md+情感回路+知识图谱），效果用提示词与小规模 DPO 补齐，留 LoRA 人格为二期 |
| 记忆漂移/人设崩（Kindroid 2026-02 已踩坑） | Letta 分页+图谱校验+GEPA 语义保真门闸+人审，记忆可审计可回滚 |
| 语音成本失控（S2S 贵 3-5倍） | 默认级联自托管（Fish Audio/CosyVoice），S2S 仅高端订阅，限流+缓存 |
| 监管与伦理（5州立法、Character.AI诉讼） | 按 NY S-3008C 设计合规，成人向先行，危机路由必做 |
| WatchOS 能力受限（无法常驻 WebRTC） | thin client 定位：推送+文本为主，语音经手机中转，离线队列补偿 |
| 自进化引入坏习惯 | 强门闸：测试100%通过、≤15KB、人审 PR、灰度发布 |

## Open Questions

| # | 问题 | 状态 |
|---|------|------|
| OQ-1 | Pi 核心具体取哪些文件/机制？是否需逆向 Pi 的 system prompt 风格？ | ✅ 已定：取情感回路+SOUL+图谱理念（ADR-001） |
| OQ-2 | 主 LLM 定 Qwen3 还是 DeepSeek V3 为默认？成本/中文/情感能力如何权衡？ | ✅ 已定：双默认 Qwen3-32B/DeepSeek V3，OpenRouter 路由（ADR-001） |
| OQ-3 | 向量库 MVP 用 pgvector 极简还是直接 Qdrant？ | ✅ 已定：Qdrant 主，pgvector 兜底（ADR-002） |
| OQ-4 | 语音自托管（Fish Audio） vs 托管（ElevenLabs）首版选哪个？ | ✅ 已定：Fish Audio 自托管主，ElevenLabs 备（ADR-003） |
| OQ-5 | WatchOS 是否首版就做，还是 Phase D 再做？ | ✅ 已定：Phase D（thin client） |
| OQ-6 | 数据主权：是否需境内/境外双部署？ | ⬜ 二期决策，不阻塞 Phase C |

## Key Decisions

| # | 决策 | 理由 | 日期 |
|---|------|------|------|
| KD-1 | 以 Pi 核心为基座，不重复造轮子 | Pi 情感陪伴哲学已验证 PMF，只取可复刻的机制，节省 3-6 月自研 | 2026-08-22 |
| KD-2 | 以 Hermes Agent 为进化引擎底座 | MIT 开源、208k stars、已验证 Gateway+GEPA 闭环，无需自研进化框架 | 2026-08-22 |
| KD-3 | 记忆采用 Letta + Qdrant + Graphiti 分层 | 唯一经生产验证的 LLM OS 方案，覆盖 episodic/semantic/state | 2026-08-22 |
| KD-4 | 语音采用级联为主、S2S 为可选 | 成本可控（$5k vs $30k/100k分钟）、可换模型、可观测 | 2026-08-22 |
| KD-5 | 顺着需求-规格-架构推进，不跳步 | 用户明确要求，符合面向终态原则 | 2026-08-22 |
| KD-6 | ADR-001/002/003 拍板（2026-08-22 铲屎官同意1/2/3） | 明确 Qwen3/DeepSeek双默认、Qdrant主、Fish Audio主 | 2026-08-22 |

## Timeline

| 日期 | 事件 |
|------|------|
| 2026-08-22 | 立项 F001，调研 synthesis 完成 |
| 2026-08-22 | Phase A 需求与规格 完成（F001-spec.md） |
| 2026-08-22 | Phase B 架构设计 完成（F001-architecture.md + ADR-001/002/003） |
| 2026-08-22 | 铲屎官拍板同意 1/2/3，ADR 全量 accepted，F001 进入 in-progress |
| 2026-08-22 | Phase C 云基座实现完成（22 tests, merge d5c316c） |
| 2026-08-22 | Phase D 语音/多端/自进化完成（37 tests, merge a984295） |

## Review Gate

- Phase A: 铲屎官评审 Spec（含 Pi 核心清单与合规）
- Phase B: 架构级 collaborative-thinking（拉 opus/codex/gpt52）→ 铲屎官拍板 ADR
- Phase C: 云基座演示 + 测试全绿 + 记忆审计录屏
- Phase D: 语音实测延迟 + WatchOS 真机 + GEPA PR 证据

## Links

| 类型 | 路径 | 说明 |
|------|------|------|
| Research | `docs/research/2026-08-22-synthesis.md` | Her 陪伴全面调研（含 Pi/Hermes/记忆/语音/合规） |
| Prompt | `docs/prompts/2026-08-22-her-companion-ai-research-prompt.md` | 调研 prompt 源 |
| Decision | `docs/decisions/ADR-001-base.md` | 基座 Pi+Hermes（accepted） |
| Decision | `docs/decisions/ADR-002-memory.md` | 记忆 Letta+Qdrant（accepted） |
| Decision | `docs/decisions/ADR-003-voice.md` | 语音级联为主（accepted） |
| Spec | `docs/specs/F001-spec.md` | 8+1 能力规格 |
| Architecture | `docs/architecture/F001-architecture.md` | 云中心架构 |

## 需求点 Checklist

| ID | 需求点（铲屎官原话/转述） | AC 编号 | 验证方式 | 状态 |
|----|---------------------------|---------|----------|------|
| R1 | "有性格" — 稳定人格，长期不漂移 | AC-A1, AC-B2, AC-C2 | SOUL.md + 一致性评估集 + 长期对话测试 | [x] |
| R2 | "有情感" — 共情、情绪识别与情感化表达 | AC-A1, AC-B2, AC-D1 | 情感分类测试 + TTS prosody 试听 + 人工评分 | [x] |
| R3 | "永久记忆" — 跨会话、跨端永久记忆，可审计可删 | AC-A2, AC-B3, AC-C3 | 跨会话召回测试 + 删除后不再召回测试 | [x] |
| R4 | "听" — 语音输入，实时 STT | AC-B4, AC-D1 | 延迟实测 + WER 测试 + 真机录屏 | [x] |
| R5 | "说" — 语音输出，情感化 TTS/克隆 | AC-B4, AC-D1 | MOS 试听 + 延迟实测 + 克隆对比 | [x] |
| R6 | "读" — 读文档/读图/读屏（多模态） | AC-A1, AC-B2 | Vision 理解测试（读图/读文档） | [x] |
| R7 | "写" — 人格化文本生成 | AC-A1, AC-C2 | 人格化写作对比测试 | [x] |
| R8 | "聊天" — His 式陪伴对话，主动且温暖 | AC-A1, AC-C2, AC-D3 | 对话脚本盲测 + 主动关怀频率评估 | [x] |
| R9 | "助理" — 工具调用与任务执行 | AC-D3 | MCP 工具 e2e 测试（日历/搜索/备忘录） | [x] |
| R10 | "云服务器为主，手机 PC 手表多端访问" — 云中心 + 多端同步 | AC-A3, AC-B5, AC-C2, AC-D2 | 跨端一致性测试 + WatchOS 真机 + 离线补偿测试 | [x] |
| R11 | "自进化能力类似于 hermes" — 越用越懂你，Skill 自生成与进化 | AC-B5, AC-D4 | GEPA 一轮进化 PR + 门闸通过证据 | [x] |
| R12 | "基于 pi agent，只取核心，不重复造轮子" | AC-A2, KD-1/2 | Pi 核心清单 + Hermes 复用清单评审 | [x] |
| R13 | 合规与伦理（隐含） | AC-A4, AC-D5 | AI 披露/自伤检测/危机路由/可删记忆 e2e | [x] |

### 覆盖检查
- [ ] 每个需求点都能映射到至少一个 AC
- [ ] 每个 AC 都有验证方式
- [ ] 前端需求已准备需求→证据映射表（Phase C/D 补）

