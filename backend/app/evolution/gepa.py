import uuid

prs: list[dict] = []


def run_gepa(user_id: str):
    # mock GEPA: mutate SOUL variant, evaluate — real file output for F002
    import pathlib

    variant = "# SOUL optimized via GEPA mock\n温暖+主动\n> based on traces for " + user_id
    assert len(variant.encode()) <= 15 * 1024
    score = 0.9
    pr_id = str(uuid.uuid4())
    pr = {
        "pr_url": f"mock-pr://{pr_id}",
        "score": score,
        "variant": variant,
        "user_id": user_id,
        "gate": {"tests": "pass", "size": "ok", "semantic": "preserve"},
        "file": f"evolution/prs/{pr_id}.md",
    }
    prs.append(pr)
    # write real file for audit
    try:
        p = pathlib.Path(f"evolution/prs/{pr_id}.md")
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(f"# GEPA PR {pr_id}\n\nUser: {user_id}\nScore: {score}\n\n```\n{variant}\n```\n", encoding="utf-8")
    except Exception:
        pass
    return pr


def list_prs():
    return prs
