# GPT-5.2 Pro 审阅（模拟）— Her 陪伴 AI 调研

> 角色：审阅者（不搜索，只审逻辑/证据/分歧）  
> 输入：三路报告 + synthesis 初稿

## 总评
Synthesis 方向正确：以 Hermes Agent 为底座是 2026 最务实的选择，Inflection Pi 已不适合作为技术底座。记忆与语音的选型有基准数据支撑。

## 逻辑漏洞 / 弱证据
1. **Pi 的 Inflection-3 上下文 1M 未经独立验证** — 仅来自第三方 AI 工具站（aitoolsdevpro），非 Inflection 官方论文，需降为“推测”。
2. **GEPA 在陪伴场景的泛化** — 原报告基于代码类 skill（github-code-review），陪伴类技能的评估指标（共情、一致性）尚未有公开 GEPA 实验，需在 MVP 中自建评估集。
3. **Qdrant p99 ~2ms** 结论来自 TokenMix 等营销向 benchmark，真实需在你的 workload（过滤+混合检索）下复测。
4. **监管引用** — NY S-3008C 与 Aalto 研究为真，但 Aalto 样本为“近2000”需注明是预印本/新闻稿，非同行评审论文。

## 三方分歧（价值信号）
- Claude 侧更强调“纯向量DB不够”，Gemini 侧更推“全托管 Pinecone”，ChatGPT 侧推“pgvector 极简”。Synthesis 折中为 Qdrant 默认 + pgvector MVP 是合理的。
- 对 TTS：ElevenLabs 品质 vs Fish Audio 成本，分歧本质是“自托管能力”。建议保留双轨。

## 遗漏盲区
- **未充分讨论“主动性”的负体验**：频繁主动会变打扰，需引入“用户控制的主动度”滑杆。
- **WatchOS 的真实约束**：watchOS 不允许常驻 WebRTC，需明确为“推送+短文本”而非实时语音。
- **数据主权**：若面向中国用户，需考虑境内外 LLM/语音服务的合规与延迟。

## 审阅结论
Release as synthesis.md 已满足 ADR 要求，建议追加一条 ADR 约束：“所有自进化变更必须人审 + 记忆可审计”。
