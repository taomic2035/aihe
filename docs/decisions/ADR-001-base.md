# ADR-001: 基座选型 — Pi 核心 + Hermes Agent

> Date: 2026-08-22 | Status: proposed | Deciders: spark + 铲屎官

## Context
需在 0-1 做出 Her 式陪伴，需兼顾情感陪伴哲学与可持续自进化。Inflection Pi 有哲学但闭源且停滞；Hermes Agent 有可验证的自进化与多端网关。

## Decision
- **Pi 只取核心**：情感优先对话、递归情感回路、知识图谱记忆理念、prosody 适配 — 以 `SOUL.md` + 提示词 + 轻量 DPO 实现，不依赖 Pi 权重/API。
- **Hermes 为底座**：直接复用 `NousResearch/hermes-agent`（MIT）作为 Agent runtime（Gateway/Skills/Memory/多平台），复用 `hermes-agent-self-evolution`（DSPy+GEPA）为进化引擎，不自研。
- **LLM 路由**：OpenRouter 统一入口，默认 Qwen3-32B / DeepSeek V3（中文/成本），Pro 可切 GPT-5/Claude 4。

## Consequences
- 正：最短路径，不重复造轮子；进化能力 $2-10/次，无需 GPU 训练。
- 负：需跟进 Hermes 版本迭代（0.18+节奏快）；Pi 情感效果需自建评估集验证。

## Alternatives Considered
- 全自研 Agent 框架 → 否，重且无进化闭环
- 纯 Pi API → 否，创新停滞且不可控
- LangGraph/CrewAI 为底座 → 可，但无现成 GEPA 进化，需自接
