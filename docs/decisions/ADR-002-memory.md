# ADR-002: 记忆选型 — Letta + Qdrant + Graphiti

> Date: 2026-08-22 | Status: accepted | Approved: 2026-08-22

## Context
永久记忆是陪伴的第一留存因子，需同时解决 episodic/semantic/state 三层，纯向量DB不够。

## Decision
- **Runtime**：Letta（ex-MemGPT，Apache-2.0）LLM OS 分页（Core/Archival/Recall），Agent 自主函数调用管理记忆。
- **向量**：Qdrant（Rust, Apache-2.0）为主，p99~2ms，HNSW+混合检索，payload 带时间/情感/重要度。
- **图谱**：Graphiti/Zep 时序知识图谱，存实体关系与演变。
- **保底**：Postgres pgvector 作为兜底/本地极简选项。
- **审计**：memory_audit 表，用户可看/删，删除同步向量+图。

## Consequences
- 正：唯一经生产验证的分层方案，Nomi 23/25、Kindroid 分级已证明路径。
- 负：三件套运维复杂度高于单 pgvector；需自建 300 条陪伴评估集。

## Alternatives
- Mem0 轻量层 → 可替换 Letta，适合不想上重运行时的团队，已保留接口抽象
- Pinecone 托管 → 若不想运维可切，接口已抽象
- Milvus → >100M 向量才需要，首版不取
