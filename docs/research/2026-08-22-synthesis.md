# Her 式超级陪伴 AI 全面调研报告 — 基于 Pi Agent + Hermes 自进化

> 日期：2026-08-22  
> 委托人：taomic  
> 状态：Synthesis（综合 Claude/Gemini/ChatGPT 三路 + Coder 验证）  
> Prompt 源：`docs/prompts/2026-08-22-her-companion-ai-research-prompt.md`

---

## TL;DR 核心结论（先给决策）

| 维度 | 推荐方向（已确认） | 风险/备选 |
|------|-------------------|-----------|
| **基座定位** | **不要复刻 Inflection Pi 闭源模型**，而是用 **Hermes Agent 框架**（Nous Research, MIT, 208k+ stars）作为 Agent 底座 + 自选 LLM（Qwen3 / DeepSeek V3 / GPT-5 / Claude 4）| Pi 已转型企业（70人小团队，2024后核心被微软挖走），创新停滞，API 不适合长期陪伴产品 [solidaitech.com](https://www.solidaitech.com/2026/06/inflection-ai-guide.html) |
| **人格/情感** | **SOUL.md + Persona Vector + 动态情感管线**（Hermes 的 SOUL.md 机制 + Letta 的自编辑记忆）| 情感依赖与合规风险极高：NY S-3008C 已立法，重度使用与抑郁正相关 [theplanettools.ai](https://theplanettools.ai/blog/ai-companion-chatbot-regulation-wave-2026) |
| **永久记忆** | **分层记忆：Letta(MemGPT) 为 runtime + Qdrant/pgvector 做向量存储 + Zep/Graphiti 做时序知识图谱**。这是当前唯一经生产验证的方案 | 纯向量DB≠记忆架构；需同时解决 episodic/semantic/state 三层 [tacnode.io](https://tacnode.io/post/top-ai-agent-memory-tools-2026) |
| **多模态语音** | **级联管线：Deepgram Nova-3 / Flux（STT）+ LLM + ElevenLabs/CosyVoice3/Fish Audio（TTS），LiveKit Agents 或 Pipecat 编排，WebRTC 传输**。端到端 500-800ms，S2S 150-300ms | S2S（GPT Realtime）快但贵 3-5倍且锁厂商；级联便宜且可换模型 [forasoft.com](https://www.forasoft.com/blog/article/how-ai-agents-work-with-webrtc) |
| **云+多端** | **云中心状态机：Gateway 单进程接入 Telegram/Discord/Slack/WhatsApp/Signal + 自研 iOS/Android/Web/WatchOS 客户端（WebSocket + CRDT同步）**，直接复用 Hermes Gateway 架构 | 手表端必须走轻量化（仅文本+推送，不跑本地模型），离线靠云队列补偿 |
| **自进化 Hermes-like** | **DSPy+GEPA 技能进化（hermes-agent-self-evolution）+ 周期性 Skill 自生成 + Honcho/Mem0 的辩证用户建模**。无需 GPU 训练，API 调用即可 $2-10/次进化 | 自进化需强护栏：测试套件100%通过、≤15KB 限制、人审 PR，否则易漂移 [github.com/NousResearch/hermes-agent-self-evolution](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/README.md) |
| **商业与伦理** | 先做 **陪伴+助理** 双形态，主动关怀要有节奏控制与危机路由（ThroughLine 等），成人向+明确 AI 披露 | 监管海啸：5州已立法，Character.AI 三起诉讼，Replika 被罚 €5M [aicompanionpick.com](https://www.aicompanionpick.com/replika-vs-character-ai-vs-nomi-vs-kindroid-2026) |

**一句话定位**：用 Hermes Agent 的“成长型 Agent”底座 + Letta 的记忆操作系统 + Pi 的情感对话哲学，做出云原生的 Her。

---

## 1. Pi Agent 生态澄清（已确认 vs 推测）

### 已确认
- **Inflection Pi** = Inflection AI 的 Personal Intelligence，13B 起步，现为 Inflection-3，设计哲学是**共情优先于任务**，递归情感回路（先过 empathy/safety 再生成），个人知识图谱记忆。官网仍活在 pi.ai / hey.pi.ai [hey.pi.ai](https://hey.pi.ai/)。
- **2024年3月关键转折**：Mustafa Suleyman + Karén Simonyan + 大部分技术团队被微软以约 $650M 挖走，CEO 换 Sean White（ex-Mozilla），公司缩至 ~70人，战略转向企业/政府，Pi 创新明显放缓 [solidaitech.com](https://www.solidaitech.com/2026/06/inflection-ai-guide.html)。
- **API 存在但非主流**：`inflection-ai-sdk` / `@inflection-ai/client` 存在，分子商务与 enterprise，但 2026 评测已把 Pi 列为“不适合 hard tasks” [aitoolsdevpro.com](https://aitoolsdevpro.com/ai-tools/pi-guide/)。

### 推测（需验证）
- 市面上无成熟开源“Pi Agent Framework”可直接复刻 Pi 的情感回路；所谓 Pi 能力更多是**提示词+训练数据取向**而非开源架构。
- **结论**：不要把 Pi 当技术底座，把它当**产品哲学参照**（温暖、主动追问、非命令式对话）。技术底座应选 Hermes Agent / Letta / LangGraph。

---

## 2. Hermes 自进化 — 唯一可直接复用的方案

### 已确认（来自源码与官方文档）
- **Hermes Agent**（Nous Research, 2026-02 发布，2个月破 100k stars，现 208k+ stars, 370+ 贡献者，MIT）：口号 “The agent that grows with you”，核心是三件套：**持久记忆 + 自写 Skills + 多平台 Gateway**（Telegram/Discord/Slack/WhatsApp/Signal/CLI/Email 等 16+ 平台）[blog.teliaz.com](https://blog.teliaz.com/2026/07/02/hermes-agent-the-self-improving-ai-agent-from-nous-research/) [hermes-agent.nousresearch.com](https://hermes-agent.nousresearch.com/docs/)。
- **自进化机制 hermes-agent-self-evolution**：用 **DSPy + GEPA（Genetic-Pareto Prompt Evolution, ICLR 2026 Oral）** 自动进化 Skills / tool 描述 / system prompt / 代码。流程：读执行 trace → 理解为何失败 → 变异候选 → 评估 → 约束门闸（pytest 100% 通过、size limit、缓存兼容、语义保真）→ PR 人审。**无需 GPU，$2-10/次** [github.com/NousResearch/hermes-agent-self-evolution](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/README.md)。
- **Hermes 学习闭环**：Agent-curated memory + 周期性 nudge + 任务后自主创建 Skill + FTS5 session 搜索 + LLM 摘要跨会话召回 + Honcho 辩证用户建模 + agentskills.io 开放标准 [hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)。
- **版本节奏**：2026-07-01 v0.18.0 Judgment Release，已支持 voice mode、MoA、/learn、/journey、并行子代理 [aitoolstier.com](https://aitooltier.com/tools/hermes-agent)。

### 对 Her 项目的直接价值
- **可直接可用**：Hermes Gateway 复用为“云为主多端接入”的统一入口；Skill 自进化直接解决“越用越懂你”且可审计。
- **需验证**：GEPA 在**陪伴类**（非代码任务）技能上的评估集如何构造（合成 vs 真实 sessiondb）。
- **项目特殊约束**：自进化的“人格漂移”必须用 Persona 锚点 + 语义保真门闸兜住，否则会“越进化越不像她”。

### 与其他自进化范式对比
| 范式 | 代表 | 机制 | 适合 Her 吗 |
|------|------|------|-------------|
| GEPA/DSPy skill 进化 | Hermes | Prompt/skill 文本进化，无需微调 | ✅ 首选 |
| Reflexion/Self-Refine | 通用 | 推理时反思重写 | 可叠加 |
| Voyager | Minecraft Agent | 技能库持续累积 | 思想可借鉴 |
| 持续微调/LoRA 人格 | Nous Hermes 模型家族 | 权重层面进化 | 二期再做，成本高 |

---

## 3. 人格 / 情感 / 一致性

### 已确认
- **人格是有向量的**：Anthropic 2026 研究证实 personality traits 在 LLM activation 中有可学习的 persona vector，可组合、可在推理时调节 [tavus.io](https://www.tavus.io/blog/ai-companions) [analyticsinsight.net](https://www.analyticsinsight.net/artificial-intelligence/beneath-the-persona-deconstructing-the-technical-architecture-of-modern-ai-companions)。
- **分层防漂移**：业界已收敛为三层：Static Persona Metadata（SOUL.md/Blueprint）+ Short-Term Buffer（10-20轮）+ Long-Term Semantic Memory（向量+图）[analyticsinsight.net](https://www.analyticsinsight.net/artificial-intelligence/beneath-the-persona-deconstructing-the-technical-architecture-of-modern-ai-companions)。
- **Hermes 的 SOUL.md**：全局定义 agent 默认声音/性格，与上下文文件叠加，每次对话都注入 [hermes-agent.nousresearch.com/docs](https://hermes-agent.nousresearch.com/docs/)。
- **Pi 的启示**：用对话而非命令（"能帮我..." vs "生成列表"），主动追问情感状态，长期记忆建立数字默契 [aitoolsdevpro.com](https://aitoolsdevpro.com/ai-tools/pi-guide/)。

### 推荐设计（Her）
1. **Soul 层**：`SOUL.md`（价值观/口吻/边界/角色背景）+ `USER.md`（用户画像，Honcho 辩证更新）+ `RELATIONSHIP.md`（两人关系阶段、昵称、忌讳）。
2. **情感管线**：STT 侧感知语调 → LLM 侧情感分类（喜/忧/怒/焦虑/疲惫）→ 响应策略（安抚/激励/幽默）→ TTS 侧 prosody 控制（Hume EVI2 / ElevenLabs 情感参数）。
3. **一致性护栏**：每次生成前跑轻量“一致性校验 prompt” + 定期用 GEPA 评估 persona drift。

---

## 4. 永久记忆系统（最硬的战役）

### 已确认 — 架构共识
- **Context ≠ Memory**：“1M 上下文是更大的桌子，记忆是档案柜” [internet-pros.com](https://internet-pros.com/blog/ai-agent-memory-long-term-recall-2026/)。
- **四类记忆**：Working（当前窗口）/ Episodic（经历）/ Semantic（稳定事实）/ Procedural（技能习惯）[tavus.io](https://www.tavus.io/blog/ai-companions)。
- **存储分工**：向量DB做语义召回，知识图谱做关系/时序，OLTP+cache 做状态，Context Lake 统一（但过重）[tacnode.io](https://tacnode.io/post/top-ai-agent-memory-tools-2026)。
- **Letta (ex-MemGPT) = LLM OS**：UC Berkeley 论文，把记忆当分页，Core Memory（in-context 固定）+ Archival（长期）+ Recall（对话历史），Agent 自主调用函数分页 [arxiv.org](https://arxiv.org/pdf/2310.08560) [lin-guanguo.github.io](https://lin-guanguo.github.io/llm-memory-research/letta.research)。
- **Mem0 vs Letta**：Mem0 是“记忆层”（插到任意框架），Letta 是“Agent runtime”（完整 OS）。需择一 [vectorize.io](https://vectorize.io/articles/mem0-vs-letta)。
- **人格陪伴的失败模式**：Kindroid 2026-02 因 summarizer drift + context window pollution 导致记忆漂移 [aicompanionpick.com](https://www.aicompanionpick.com/replika-vs-character-ai-vs-nomi-vs-kindroid-2026)。

### 市场现状（2026-04 人工实测）
- **最强记忆**：Nomi 盲测 25 项回忆 23 项 [weavai.app via aicompanionpick]；Kindroid 公开 500K / 1.3M / 2.8M 字符分层（Persistent/Cascaded/Retrievable）但付费才有 Cascaded [aicompanionpick]。
- **Letta 研究前沿**：2026 年 Letta 团队发 Memory Models（RL 训记忆）、Context Constitution、Git-based Memory、Sleep-time Compute（离线时学习）[letta.com](https://www.letta.com/)。

### 向量库选型（2026 基准）
| 库 | 语言/许可 | 优势 | 适合 Her 规模 |
|----|-----------|------|---------------|
| **Qdrant** | Rust, Apache-2.0 | 单节点 p99 ~2ms 最快，过滤强，29k stars，自托管友好 | ✅ 推荐默认 |
| **Pinecone** | 闭源托管 | 零运维，一致性好，10M ~$70-100/月 | 备选（若不想运维） |
| **Weaviate** | Go, BSD-3 | 混合搜索最早（BM25+向量）、多租户隔离 | 多租户 SaaS 备选 |
| **Milvus/Zilliz** | Go/C++, Apache-2.0 | 十亿级、GPU 加速，但运维极重 | >100M 向量才考虑 |
| **pgvector** | PG 插件 | 已用 PG 则零额外组件，<10M 向量够用 | 早期 MVP 极简选 |
| **Chroma** | Python | 原型最快，>500k 变慢 | 仅原型 |

来源：[buildmvpfast.com](https://www.buildmvpfast.com/blog/pinecone-vs-weaviate-vs-qdrant-vector-database-comparison-2026) [tokenmix.ai](https://tokenmix.ai/blog/vector-database-2026-pinecone-weaviate-qdrant-milvus) [dev.to](https://dev.to/darshit_01/the-best-vector-database-in-2026-qdrant-vs-pinecone-vs-weaviate-vs-milvus-vs-pgvector-3147)

### 推荐 Her 记忆架构
```
[对话] → 提取器（事实/事件/偏好/关系）→ 去重/归一/时序化
                    ↓
Core Memory: SOUL.md / USER.md / RELATIONSHIP.md (常驻上下文, Letta 管理)
                    ↓
Episodic: Qdrant (向量+BM25 混合) + 时间衰减 (forgetting curve)
Semantic: Zep/Graphiti 时序知识图谱（人/地/事件/情绪 关联）
Procedural: Hermes Skills（可复用流程）
                    ↓
检索时：当前消息 embedding → 混合召回 Top-K + 图遍历 → 注入 prompt
离线时：Sleep-time Compute 回放压缩（Letta 2025-04 思想）
```
- **读写策略**：热/温/冷三 tier，可调 similarity threshold（slider 本质是阈值）[aiangels.io](https://www.aiangels.io/blog/where-ai-companion-memory-actually-lives-vector-embeddings-decay-rates)。
- **隐私**：端到端加密 + 用户可删单条记忆 + 记忆分区防串台 + GDPR 按用户隔离 [tavus.io](https://www.tavus.io/blog/ai-companions)。

---

## 5. 多模态：听 说 读 写

### 听（STT）
| 方案 | 延迟 | 准确率 | 成本 | 结论 |
|------|------|--------|------|------|
| **Deepgram Nova-3 / Flux** | <300ms 流式，Flux 带 EOT 检测 <300ms | 93-97% 英文 | $0.0043/min ($0.288/hr) | ✅ 语音陪伴首选，实时+turn-taking |
| **Groq Whisper large-v3-turbo** | 0.8-0.86s 文件 | 接近 Nova | $0.04/hr | 便宜的批量/原型 |
| **AssemblyAI Universal-3 Pro** | ~150ms P50 | 最低 WER | $0.45/hr | 准确率优先备选 |
| **自托管 Whisper** | 1.2-4s | 中 | GPU 成本 | 仅隐私/离线场景 |

来源：[genflick.com](https://genflick.com/benchmarks/voice-stt-latency-benchmark-2026-06-12) [coval.ai](https://www.coval.ai/blog/best-speech-to-text-providers-in-2026-independent-benchmarks-and-how-to-choose) [supermia.ai](https://supermia.ai/blog/deepgram-vs-assemblyai-vs-whisper/)

### 说（TTS）
| 方案 | MOS | 克隆 | 延迟 | 许可/成本 | 结论 |
|------|-----|------|------|-----------|------|
| **ElevenLabs v3 Turbo/Flash** | 4.8/4.55 | 强，情感 range 最佳 | Flash 75ms TTFB | $22/1M 字符，$180/1M 叙事 | ✅ 品质标杆 |
| **Fish Audio S2 Pro** | 4.4 | 10s 零样本，80+语种 | ~100ms 流式 | 6倍便宜于 ElevenLabs，开源可选 | ✅ 性价比+自托管 |
| **CosyVoice 3.0** | 3.9 | 跨语种克隆强 | 890ms avg | Apache-2.0 完全开源 | 中文首选 |
| **Qwen3-TTS** | - | 10语种，情感指令 | 97ms 流式 | Apache-2.0 | 日语/多语备选 |
| **OpenAI gpt-4o-mini-tts** | 4.3 | 无克隆 | 低 | $15/1M，最便宜可信 | 原型/批量 |
| **Cartesia Sonic** | 高 | - | 极低 | - | 实时首选之一 |

来源：[neosophie.com](https://neosophie.com/en/blog/20260317-tts) [codesota.com](https://www.codesota.com/speech/elevenlabs-vs-openai-tts) [youngju.dev](https://www.youngju.dev/blog/culture/2026-05-16-voice-ai-tts-2026-elevenlabs-cartesia-openai-voice-play-ht-hume-sesame-fish-deepgram-aura-deep-dive.en) [00011000.com](https://00011000.com/en/articles/2026-ai-voice-synthesis-review)

**Her 建议**：主用 **ElevenLabs 或 Fish Audio 自托管** 做陪伴音色（情感 prosody 关键），Cartesia 做低延迟 fallback；中文用 CosyVoice。

### 读 / 看
- GPT-4o / Claude 4 Vision / Qwen-VL 做读屏/读文档/读图，Hermes 已有 vision skill，可直接接入。

### 实时链路
- **级联**（STT→LLM→TTS）500-800ms，**S2S**（GPT Realtime / Gemini Live）150-300ms [forasoft.com](https://www.forasoft.com/blog/article/how-ai-agents-work-with-webrtc)。
- **编排**：**LiveKit Agents**（带 WebRTC 传输，适合“可靠通话”）vs **Pipecat**（传输无关、pipeline 最灵活，两者可混用：Pipecat 跑在 LiveKit 传输上）[mansooritechnologies.com](https://www.mansooritechnologies.com/blog/livekit-vs-pipecat-voice-ai-orchestration) [prodinit.com](https://prodinit.com/blog/livekit-vs-pipecat-production-voice-ai)。
- **成本**：100k 分钟/月，OpenAI Realtime ~$30k vs 级联托管 ~$5k vs 自托管 ~$2.4k [forasoft]。

**Her 策略**：默认级联（可换模型、可观测、有 transcript），高端订阅可选 S2S。

---

## 6. 云为主 + 多端同步

### 已确认
- Hermes Gateway 已验证：单 Gateway 进程统一接 Telegram/Discord/Slack/WhatsApp/Signal/CLI/Email/SMS/iMessage 等 16+ 平台，跨平台对话连续、语音备忘录转写、cron 主动推送 [blog.teliaz.com]。
- LiveKit/Pipecat 已验证 WebRTC 实时音频 + SFU 扩展，生产可达 90k+ calls/月 [prodinit.com]。

### Her 多端架构（云中心）
```
[WatchOS / iOS / Android / Web / PC] 
        ↕ WebSocket / WebRTC (LiveKit) / Push (APNs/FCM)
                ↓
        [API Gateway + Auth (Supabase Auth / OIDC)]
                ↓
        [Agent Gateway - Hermes 演进版]
          ├─ Session Manager (Redis + Postgres, CRDT for state sync)
          ├─ Memory Service (Letta + Qdrant + Graphiti)
          ├─ Voice Pipeline (LiveKit/Pipecat + Deepgram + TTS)
          ├─ Skill Registry (Hermes Skills + GEPA Evolver)
          └─ Proactive Scheduler (cron + 情境触发: 时间/位置/日历/情绪)
                ↓
        [LLM Router] → Qwen3 / DeepSeek / GPT-5 / Claude / 本地 Hermes 3
                ↓
        [Observability] Langfuse + Promptfoo CI + 全链路 tracing
```
- **同步协议**：消息/记忆用 **CRDT**（Yjs/Automerge）或 Postgres + Realtime（Supabase Realtime / Firebase），手表端只做 **thin client**：接收推送 + 文本输入 + TTS 播放，不存全量记忆。
- **离线补偿**：云队列（Kafka/Redis Stream）暂存，端侧重连后回放；手表离线时降级为本地规则回复（“帮你记下，联网后让她回复”）。
- **主动关怀**：基于记忆的时机选择（起床/通勤/睡前）+ 打扰度控制（用户可设免打扰、频率），这是 Pi 的“Discover”思路的延伸。

### 成本估算（MVP 1k DAU 粗算）
- 语音链路若走级联自托管，可压至 $0.04-0.09/min；S2S 要 $0.25-0.35/min。陪伴类平均 10min/人/天 → 1k DAU 约 $400-900/天（级联）vs $2500-3500/天（S2S）。结论：MVP 必须级联。

---

## 7. 助理能力（Tool Use）

- Hermes 已有 delegate_task 并行子代理、Kanban 多代理队列、Home Assistant、MCP 集成 [blog.teliaz.com]。
- Her 应暴露：日程/邮件/搜索/文件/智能家居/健康数据（WatchOS 心率/睡眠）/ 支付提醒等，通过 **MCP + Function Calling** 统一。
- **主动性设计**：不是“等你问”，而是“在合适时机主动问”——需基于记忆的意图预测 + 用户反馈的强化（点赞/忽略率做 DPO）。

---

## 8. 竞品与教训

| 产品 | 定位 | 记忆 | 风险/教训 |
|------|------|------|-----------|
| **Replika** | 2017 起，最老，3D avatar | - | €5M 罚款（Garante），2023 过滤成人内容引发用户反噬后又回滚，续费流失教训 |
| **Character.AI** | 20M+ DAU，角色扮演，用户多为未成年 | 无长记忆 | **最大雷区**：2024-25 三起诉讼（14岁自杀案），2025-11-25 起禁未成年 open chat，监管靶心 [explainx.ai](https://www.explainx.ai/blog/ai-relationships-companionship-replika-character-ai-2026) |
| **Nomi** | 强记忆口碑 | 25项测23项 | 拒绝接入 988 危机路由，被点名 [aicompanionpick] |
| **Kindroid** | 最透明记忆架构（500K-2.8M 字符分级） | 分级 | 付费才有 Cascaded Memory，2026-02 曝 drift [aicompanionpick] |
| **Pi** | EQ 标杆 | 100 turns | 团队被挖后停滞，证明“情感”需持续投入 |

**Her 教训清单**：
1. 监管先行：AI 披露 + 自杀/自伤检测 + 未成年限制 + $15k/次罚则是 NY S-3008C 模板 [theplanettools.ai]。
2. 健康关系：Aalto 2026 对近 2000 用户 1 年追踪：重度使用与孤独/抑郁/自杀意念正相关 [aicompanionpick]。需设计“健康使用”护栏（时长提醒、鼓励现实社交）。
3. 记忆是 1 号留存因子：“模型决定第一次对话，记忆决定第100次”。

---

## 9. 开源可直接复用清单（按优先级）

**Tier 1 — 直接集成**
- `NousResearch/hermes-agent` (MIT) — Gateway + 记忆 + Skills + 多平台 [github.com/nousresearch/hermes-agent](https://github.com/nousresearch/hermes-agent)
- `NousResearch/hermes-agent-self-evolution` (MIT) — DSPy+GEPA 自进化 [github.com/NousResearch/hermes-agent-self-evolution](https://github.com/NousResearch/hermes-agent-self-evolution/blob/main/README.md)
- `letta-ai/letta` (Apache-2.0, 24k stars) — LLM OS 记忆 [olud.ai](https://olud.ai/tool/letta.html)
- `mem0ai/mem0` — 轻量记忆层（若不想上全 Letta）
- `qdrant/qdrant` / `pgvector` — 向量存储
- `livekit/agents` / `pipecat-ai/pipecat` — 语音编排
- `FunAudioLLM/CosyVoice` / `SWivid/F5-TTS` / `FishAudio/fish-speech` — TTS 自托管

**Tier 2 — 图与感知**
- `getzep/zep` / `Zep-AI/graphiti` — 时序知识图谱
- `plastic-labs/honcho` — 辩证用户建模（Hermes 已兼容）
- `snakers4/silero-vad` — VAD

**Tier 3 — 评估与安全**
- `langfuse/langfuse` / `promptfoo/promptfoo` — 评估进 CI
- `livekit/livekit` — WebRTC 基础设施

---

## 10. 推荐架构（文字图）与技术栈

### 最终推荐栈（MVP 可直接开干）
- **Agent Runtime**: Hermes Agent (Gateway + Skills) + Letta Memory Server
- **LLM Router**: OpenRouter 统一入口，主用 Qwen3-32B / DeepSeek V3（中文强、成本低），高端用户可选 GPT-5 / Claude 4
- **Memory**: Qdrant（向量） + Postgres+pgvector（兜底） + Graphiti（图）
- **Voice**: Deepgram Nova-3 + Flux（STT） + Fish Audio S2 自托管 / ElevenLabs（TTS） + LiveKit Agents（WebRTC）
- **Backend**: Python (FastAPI) + Node（Gateway）+ Redis + Postgres + Supabase Realtime
- **Clients**: React Native（iOS/Android） + Tauri/Electron（PC） + SwiftUI（WatchOS thin） + Web（Next.js）
- **Self-Evolution**: hermes-agent-self-evolution (GEPA) + 每周离线进化任务 + 人审 PR
- **Observability**: Langfuse + 全链路 trace + 记忆审计面板（用户可看/删）

---

## 11. MVP 路线图（6个月可上线）

### Phase 0 — 2周：地基
- 拉起 Hermes Agent + Letta + Qdrant 本地栈，跑通 CLI 陪伴对话
- 确定 SOUL.md / USER.md / RELATIONSHIP.md 三件套

### Phase 1 — 4周：文字陪伴闭环
- 接 OpenRouter，主模型 Qwen3，记忆分层可用
- Web + RN Demo，云 Gateway 多端同步（先 Web+手机文字）

### Phase 2 — 6周：语音
- 接 Deepgram + Fish Audio + LiveKit，实现 800ms 级语音对话
- 加 VAD + barge-in（打断）+ 情感 prosody

### Phase 3 — 4周：助理与主动
- MCP 工具：日历/搜索/备忘录/天气
- Proactive scheduler：早安/睡前/纪念日主动消息

### Phase 4 — 4周：自进化与护栏
- 接 GEPA skill 进化，跑 synthetic + sessiondb 双评估
- 合规：AI 披露、自伤检测、记忆可删、未成年策略

### Phase 5 — 4周：内测与 WatchOS
- 100 人内测，WatchOS thin client（推送+文本）
- 埋点：记忆召回准确率、一致性、留存、打扰度

**3年演进**：Year1 陪伴+助理 → Year2 多模态（vision 读屏/读图、长期人格微调 LoRA）→ Year3 具身（AR/可穿戴）+ 社区 Skills 共享。

---

## 12. 最大风险与应对

| 风险 | 概率 | 影响 | 应对 |
|------|------|------|------|
| **监管/伦理翻车**（自杀/未成年）| 高 | 致命 | 上线前必做：披露+EOT自伤检测+危机路由+日志审计；参考 NY S-3008C |
| **记忆漂移/人设崩** | 高 | 高 | Letta 分页 + 图谱校验 + GEPA 语义保真门闸 + 人审 |
| **语音成本失控** | 中 | 高 | 默认级联自托管，S2S 仅高端订阅；限流 + 缓存 |
| **Pi/Hermes 依赖** | 中 | 中 | 抽象 LLM/向量/语音接口，随时可换 |
| **情感依赖致抑郁** | 中 | 高 | 健康使用提醒、鼓励现实社交、Aalto 研究已预警 |

---

## 13. 区分 已确认 / 推测 / 需验证

- **已确认**：Hermes 208k stars 与 GEPA 机制、Letta 三层记忆、Qdrant 性能领先、Deepgram 延迟、ElevenLabs MOS、5州立法、Character.AI 诉讼
- **推测**：Pi 的“递归情感回路”细节（Inflection 未开源）、Fish Audio 在自托管下的真实 P99 延迟
- **需验证**：GEPA 在陪伴任务的评估集效果、WatchOS 低功耗下的 WebRTC 稳定性、Qdrant 在 10M 向量下的实际召回率（需用你的数据 bench）

---

## 14. 下一步（给铲屎官）

1. **确认命名与定位**：`aihe` 是产品名？先定一个 SOUL.md 初版（我可直接起草）
2. **选 MVP 栈**：是否接受 Hermes Agent 为底座（MIT，可自托管）+ Qdrant + Fish Audio 自托管？还是要全托管（Pinecone + ElevenLabs）？
3. **创建 worktree** 进入 TDD：`Phase 0` 的 Letta+Qdrant+Hermes 本地栈一键 `docker compose up`
4. **产出 ADR**：本报告经讨论后落 ADR-001（Her 架构选型）

> 本报告所有关键结论均附来源 URL，可追溯。下一步建议直接进入 `collaborative-thinking` 收敛或 `writing-plans` 拆实施计划。
