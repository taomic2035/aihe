# Session Summary — aihe 项目 2026-08-22

> 关机前上下文快照。恢复时先读本文件 + `docs/ROADMAP.md` + `docs/features/`。

## 项目定位

**aihe** — 类电影 Her 的**超级陪伴 AI（已更正为 He，男性）**：有性格、情感、永久记忆、听/说/读/写、聊天、助理。云服务器为主，手机/PC/手表多端访问。基于 **Pi 核心**（只取情感对话哲学+人格一致性+知识图谱理念，不复刻闭源权重）+ **Hermes 自进化**（DSPy+GEPA）。铲屎官：taomic。执行猫：spark (Muse Spark / opencode)。

## 关键决策（全部已拍板）

- ADR-001 基座：Pi 核心 + Hermes Agent 底座 + OpenRouter（Qwen3/DeepSeek 双默认）
- ADR-002 记忆：Letta + Qdrant 主 + pgvector 兜底
- ADR-003 语音：级联为主（STT→LLM→TTS），S2S 为 Pro 可选
- **He 人设**：26岁 温暖大哥哥，男声（`persona/SOUL.md`）
- LLM 实测选定：`nvidia/nemotron-3-nano-30b-a3b:free`（OpenRouter 免费额度）
  - API Key: 见 `.env` 或 `OPENROUTER_API_KEY` 环境变量
- ASR 终态：**SenseVoiceSmall 本地**（国内直连 modelscope，M5 实测 0.82s，中文 CER 7.81%，Whisper 慢10×被否）
- TTS 终态演进：
  - 过渡已通：**Edge Yunxi 男声** `zh-CN-YunxiNeural`（1.25s 真声 MP3，最自然 0 成本）
  - Piper zh huayan 104ms 但女声机械（已否）
  - Fish S2 Pro（#1 盲测终态）：本机 pip 装 2次超时未成，留 GPU 环境再上

## 本机环境（Mac M5 10核 / 32GB / 623GB 空闲）

- 无 docker compose 插件、无 Docker.app；colima 未运行 → 全部走 Python 原生 + Feature Flag 降级
- 已装：pytest/fastapi/funasr 1.4.2/torchaudio/piper-tts/edge-tts/faster-whisper/modelscope/uvicorn
- 已下载模型：`~/.cache/modelscope/hub/models/iic/SenseVoiceSmall`（893MB）、`/tmp/piper_voices/*.onnx`（huayan/chaowen/xiao_ya）
- 注意 `/tmp` 关机会清空 → piper voices 需重新下载（`python3 -c "from piper.download_voices import download_voice; download_voice('zh_CN-huayan-medium', download_dir=Path('/tmp/piper_voices'))"`）

## Git 状态（本地 repo，无 remote）

```
main            ba674b0 → 9b84370 (Edge Yunxi provider)
worktree        /Users/taomic/vibecoding/aihe-F002-prod [feat/F002-prod] 4bb3bfe
```

## Feature 状态

### F001 His 式超级陪伴 AI — **done** ✅
- Phase A 规格 / B 架构+ADR×3 / C 云基座 / D 语音多端自进化 全部 AC 20/20 打勾
- 37 tests PASS，mock 层闭环（chat/memories/realtime/voice/watch/tools/scheduler/evolution/safety）

### F002 生产级替换 — **in-progress**（worktree feat/F002-prod, 43 tests PASS）
- ✅ AC-A1 QdrantStore 真实+降级 flag（`MEMORY_BACKEND=memory|qdrant|auto`）
- ✅ AC-A3 MEMORY_BACKEND flag 就绪（alembic 未跑）
- ⬜ AC-A2 Letta 真实
- ✅ AC-B1 SenseVoice 本地 ASR 0.82s 替代 Deepgram 方案
- ✅ AC-B2 Edge Yunxi 男声 1.25s 真声
- ⬜ AC-B3 全链路 <800ms + LiveKit + barge-in
- ⬜ AC-C1 WatchOS 真机（SwiftUI thin 代码已有 watchos/WatchSync.swift）
- ⬜ AC-C2 MCP 真 key（calendar/search/memo mock 已通）
- ✅ AC-C3 GEPA PR 文件落盘 evolution/prs/
- ⬜ AC-C4 Langfuse 真实 SDK（代码就绪需 LANGFUSE_HOST）

## 运行中的服务（关机即停）

| 服务 | 端口 | 启动命令 |
|------|------|----------|
| He 后端 | 8000 | 见下 |
| He 语音页静态 | 3000 | `python3 -m http.server 3000 --directory ~/vibecoding/aihe-F002-prod` |

**重启后端（真实 LLM + Edge 男声）：**
```bash
cd ~/vibecoding/aihe-F002-prod
export OPENROUTER_API_KEY="$OPENROUTER_API_KEY"
export LLM_MODEL="nvidia/nemotron-3-nano-30b-a3b:free"
export VOICE_PROVIDER="edge"
export EDGE_VOICE="zh-CN-YunxiNeural"
export MEMORY_BACKEND="memory"
nohup python3 -m uvicorn backend.app.main:app --host 0.0.0.0 --port 8000 > /tmp/aihe_server.log 2>&1 &
```
**测试入口：** `http://localhost:3000/he_voice.html`（Chrome/Edge，浏览器原生 ASR 中文 → He LLM → Edge 男声播放）

## 已验证的实测数据

- SenseVoiceSmall 转写 piper 合成音频：**0.79-0.82s**，输出准确（`你好，我是阿明，喜欢喝美式。`）
- Edge Yunxi TTS：**1.25s** 33KB MP3 真声
- 全链路 demo（piper女声版）：ASR 0.82 + LLM 5.41(nemotron免费限速) + TTS 1.87 = 8.1s
- He 记忆召回验证通过：说"我喜欢喝什么"必回"美式"+上海
- Safety 高危拦截 + ThroughLine 危机资源 e2e 通过
- GEPA PR 文件落盘 evolution/prs/{id}.md 通过

## 用户偏好与纪律

- 铲屎官要求：**严谨、先验证再说完成、不要预判成功**（"哪里成功了，我还没测呢"教训）
- 不重复造轮子；Pi 只取核心；按需求→规格→架构推进
- 家规：commit 带 `[spark/Muse-Spark-1.2🐾]` 签名；ROADMAP 仅 main 改；worktree 隔离开发

## 下次继续的候选任务

1. **AC-B3** 全链路延迟优化：服务端 SenseVoice 替换浏览器 ASR + 流式 TTS 首包 + barge-in
2. **AC-A2** Letta 真实接入（docker compose 或 pip letta）
3. **AC-C2** MCP 真 key（Google Calendar / Tavily / Notion）
4. **Fish S2 Pro** GPU 环境稳装（uv/conda 另起环境）
5. F002 合入 main（当前 worktree 领先 main 若干 commit，合入前需 quality-gate）

## 关键文件索引

- 人设：`persona/SOUL.md`（He 26岁温暖大哥哥）
- 架构：`docs/architecture/F001-architecture.md` + `docs/decisions/ADR-001~003`
- 规格：`docs/specs/F001-spec.md`、`docs/features/F002-prod-hardening.md`
- 计划：`docs/plans/2026-08-22-F001-phase-c-core-plan.md`、`F001-phase-d-plan.md`
- 调研：`docs/research/2026-08-22-synthesis.md`（Pi/Hermes/记忆/语音/合规全景）
- 语音页：`aihe-F002-prod/he_voice.html`
- 后端入口：`backend/app/main.py`（9 routers：chat/memories/realtime/voice/watch/tools/scheduler/evolution/safety）
