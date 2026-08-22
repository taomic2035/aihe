# 超级陪伴型 AI (Her-like) 全面调研 - 基于 Pi Agent 定制

> 委托人：taomic  日期：2026-08-22

## 背景

委托人希望基于 **Pi Agent** 定制一个类似于电影《Her》中 Samantha 的**超级陪伴型 AI**：

- **核心定位**：不是工具型助手，而是具有**性格、情感、永久记忆**的陪伴体，具备自进化能力（类似 Hermes）
- **能力要求**：听 / 说 / 读 / 写 / 聊天 / 助理（多模态交互 + 任务执行）
- **架构要求**：**云服务器为主**，支持**多客户端同步访问**（手机 / PC / 手表等）
- **关键特质**：长期记忆、情感连续性、主动性、个性化、人格一致性、自进化
- **对标**：Inflection Pi 的情感陪伴特性 + Her 的沉浸感 + Hermes 的自进化/自我改进能力

目前 workspace 为空（`aihe` 为全新项目），需要从 0 到 1 的技术选型与架构设计依据。

> 名词澄清：
> - **Pi Agent**：需调研是否指 Inflection AI 的 Pi（情感化 AI）及其开源复刻/架构，或指其他名为 Pi 的 Agent 框架（如 PI agent framework）。需覆盖两类可能性。
> - **Hermes 自进化**：可能指 Nous Research Hermes 模型的自我改进/微调能力，或泛指 Agent 的自我反思、自我进化（Self-Evolving Agent / Self-Improvement）范式。需两者都调研。

## 需要调研的问题

### 1. Pi Agent 生态与基座选型
- Pi (Inflection AI) 的架构、性格/情感设计理念、对话策略、开源复刻项目有哪些？（如 Pipecat, OpenPi 等）
- 主流 Agent 框架对比：LangGraph / CrewAI / AutoGen / OpenAgents / Pi-agent 框架等，哪个最适合做 Her-like 陪伴？
- 基座大模型选型：闭源（GPT-5, Claude 4, Gemini 2.5）vs 开源（Llama 3, Qwen3, DeepSeek V3, Hermes 3/4）用于陪伴场景的情感/角色扮演能力排名？

### 2. 人格 / 情感 / 角色一致性
- 如何设计可持久、可进化的人格系统（Personality System）？业界方案：Character.ai, Replika, Pi, Soul AI
- 情感计算（Affective Computing）最新进展：情感识别、情感生成、共情对话（Empathetic Dialogue）
- 角色一致性与长期人设不崩（Persona Consistency）如何保障？System Prompt vs Fine-tuning vs LoRA 人格

### 3. 永久记忆系统（Long-term Memory）
- 记忆分层架构：短期/中期/长期/永久记忆如何设计？（MemGPT / Letta, MemoryBank, Memory3, Generative Agents）
- 向量数据库选型：Pinecone / Qdrant / Milvus / Chroma / Supabase pgvector 在长期记忆场景的对比
- 知识图谱 + RAG 结合做人物关系/事件记忆（如 GraphRAG, NebulaGraph）
- 记忆的遗忘/压缩/提炼/反思机制（Reflection, Summarization）
- 永久记忆的隐私与合规（GDPR, 数据主权）

### 4. 多模态交互：听 说 读 写
- **听（ASR/STT）**：Whisper v3 / Deepgram / ElevenLabs STT / 通义听悟 实时性与准确率对比
- **说（TTS）**：ElevenLabs / OpenAI TTS / Fish Audio / CosyVoice / GPT-SoVITS 克隆音色与情感语调
- **读（Vision/Document）**：多模态理解（GPT-4o, Claude Vision, Qwen-VL）用于读屏幕/读文档/读图
- **写（生成）**：文本生成的人格化调优
- 实时语音对话链路（STT -> LLM -> TTS）延迟优化：Pipecat, LiveKit, Daily.co, WebRTC 方案
- 端侧 vs 云侧语音处理权衡

### 5. 云为主 + 多端同步架构
- 云服务器架构：中心化状态管理、Session 同步、消息队列、WebSocket/ SSE 长连接
- 多客户端（iOS/Android/PC/Web/WatchOS）统一协议与数据同步：CRDT, Operational Transform, Supabase Realtime, Firebase
- 离线/在线混合策略，手表等低功耗端如何轻量化接入
- 推送与主动关怀（Proactive Interaction）：时机选择与打扰度控制
- 成本与规模化：推理成本、并发、流式响应

### 6. 自进化能力（Self-Evolution / Hermes-like）
- Hermes 模型的自进化机制是什么？（Nous Hermes 持续微调、自我合成数据）
- Self-Evolving Agent 范式：Voyager / Reflexion / Self-Refine / Generative Agents / ADAPT
- 记忆驱动的个性进化：基于用户反馈的 RLHF / DPO / 自我反思微调
- 如何做到“越用越懂你”且不漂移？评估指标与护栏
- 长期进化的安全与对齐（Alignment）风险

### 7. 助理能力（Agent / Tool Use）
- 工具调用与任务执行：日程、邮件、搜索、文件操作、智能家居
- MCP (Model Context Protocol), Function Calling, Open Interpreter 对比
- 主动性（Proactivity）设计：何时主动发起对话/建议

### 8. 竞品与产品形态
- 陪伴类 AI 产品全景：Replika, Character.AI, Pi, Soul Gen, Heeyo, Poly.ai, 卿我AI, Glow
- Her-like 产品的失败教训与成功要素（用户留存、情感依赖风险）
- 商业模式与伦理边界

### 9. 技术路线建议与风险
- MVP 最小可行架构推荐（6个月内可上线）
- 3年演进路线图
- 最大技术风险与备选方案
- 开源可复用项目清单

## 输出要求
- 每个结论标注信息来源（URL 或文档名），区分“已确认”和“推测”
- 给出**推荐方向 + 风险**，而非罗列选项
- 包含架构图（文字描述即可）的建议
- 列出可直接复用的开源项目与论文（带链接）
- 明确哪些适合“直接可用”、哪些“需验证”、哪些受“项目特殊约束”

## 参考资料
- 当前 workspace：`/Users/taomic/vibecoding/aihe`（空项目，0 代码）
- 用户关键词：Pi agent, Her, 永久记忆, 自进化 Hermes, 云+多端
