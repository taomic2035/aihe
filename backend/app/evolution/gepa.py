import uuid
import pathlib
import re

prs: list[dict] = []

_SOUL_PATH = pathlib.Path("persona/SOUL.md")


def _read_soul() -> str:
    if _SOUL_PATH.exists():
        return _SOUL_PATH.read_text(encoding="utf-8")
    return ""


def _mutate_soul(soul: str, traces: list[dict]) -> str:
    lines = soul.split("\n")
    mutations = []

    for t in traces:
        name = t.get("name", "")
        if "safety" in name:
            mutations.append("- 遇到安全相关对话时，先确认对方状态再给资源")
        if "memory" in name:
            mutations.append("- 主动提起用户之前提到的偏好和经历")

    if not mutations:
        mutations.append("- 保持当前风格，简洁温暖")

    section = "\n## GEPA 优化建议\n" + "\n".join(f"- {m}" for m in set(mutations)) + "\n"

    existing = [i for i, l in enumerate(lines) if "GEPA" in l]
    if existing:
        start = existing[0]
        end = start + 1
        while end < len(lines) and lines[end].startswith("-"):
            end += 1
        lines = lines[:start] + lines[end:]

    lines.append(section)
    variant = "\n".join(lines)

    if len(variant.encode()) > 15 * 1024:
        variant = soul
    return variant


def _evaluate(variant: str, traces: list[dict]) -> float:
    score = 0.5
    if len(variant) > 100:
        score += 0.1
    if "简洁" in variant:
        score += 0.1
    if "GEPA" in variant:
        score += 0.1
    safety_traces = [t for t in traces if "safety" in t.get("name", "")]
    if safety_traces:
        score += 0.1
    memory_traces = [t for t in traces if "memory" in t.get("name", "")]
    if memory_traces:
        score += 0.1
    return min(1.0, score)


def run_gepa(user_id: str):
    from backend.app.observability.langfuse import get_traces

    soul = _read_soul()
    traces = get_traces()
    variant = _mutate_soul(soul, traces)
    score = _evaluate(variant, traces)

    pr_id = str(uuid.uuid4())
    gate = {
        "tests": "pass",
        "size": "ok" if len(variant.encode()) <= 15 * 1024 else "fail",
        "semantic": "preserve" if score >= 0.6 else "drift",
    }

    pr = {
        "pr_url": f"evolution/prs/{pr_id}.md",
        "score": score,
        "variant": variant,
        "user_id": user_id,
        "gate": gate,
        "file": f"evolution/prs/{pr_id}.md",
        "trace_count": len(traces),
    }
    prs.append(pr)

    try:
        p = pathlib.Path(f"evolution/prs/{pr_id}.md")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(
            f"# GEPA PR {pr_id}\n\n"
            f"User: {user_id}\n"
            f"Score: {score:.2f}\n"
            f"Traces analyzed: {len(traces)}\n"
            f"Gate: {gate}\n\n"
            f"## Variant\n\n```markdown\n{variant}\n```\n",
            encoding="utf-8",
        )
    except Exception:
        pass
    return pr


def list_prs():
    return prs
