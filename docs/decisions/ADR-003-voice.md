# ADR-003: 语音选型 — 级联为主，S2S 为高端可选

> Date: 2026-08-22 | Status: accepted | Approved: 2026-08-22

## Context
Her 的沉浸感依赖语音，需在延迟、品质、成本、可观测间权衡。

## Decision
- **编排**：Pipecat 跑在 LiveKit Transport 上，WebRTC 传输。
- **STT**：Deepgram Nova-3（流式 <300ms）+ Flux 语义 EOT + Silero VAD。
- **TTS**：主 Fish Audio S2 自托管（~100ms, 可克隆, 80+语种），备 ElevenLabs Flash（75ms TTFB, MOS 4.8），中文 CosyVoice 3.0。
- **策略**：默认级联（STT→LLM→TTS）p50<800ms，高端 Pro 可选 S2S（GPT Realtime 150-300ms）。
- **成本**：级联 $5k/100k分钟 vs S2S $30k/100k分钟，首版级联为主。

## Consequences
- 正：成本可控、可换模型、有 transcript 可观测、支持打断。
- 负：级联延迟高于 S2S，需精细调优 VAD/流式与 LLM 首字时间。

## Alternatives
- 纯 S2S（OpenAI Realtime）→ 快但贵且锁厂，已作为 Pro 选项保留
- 自托管 Whisper → 延迟 1-4s，仅离线兜底
