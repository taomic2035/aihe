import uuid

prs: list[dict] = []


def run_gepa(user_id: str):
    # mock GEPA: mutate SOUL variant, evaluate
    variant = "# SOUL optimized via GEPA mock\n温暖+主动"
    # ensure size <=15KB
    assert len(variant.encode()) <= 15 * 1024
    # mock score
    score = 0.9
    pr = {
        "pr_url": f"mock-pr://{uuid.uuid4()}",
        "score": score,
        "variant": variant,
        "user_id": user_id,
        "gate": {"tests": "pass", "size": "ok", "semantic": "preserve"},
    }
    prs.append(pr)
    return pr


def list_prs():
    return prs
