import uuid

store: dict[str, dict] = {}


def create_job(user_id: str, cron: str, trigger: str):
    jid = str(uuid.uuid4())
    job = {"id": jid, "user_id": user_id, "cron": cron, "trigger": trigger, "enabled": True}
    store[jid] = job
    return job


def list_jobs(user_id: str):
    return [j for j in store.values() if j["user_id"] == user_id]


def patch_job(jid: str, enabled: bool | None = None):
    if jid not in store:
        return None
    if enabled is not None:
        store[jid]["enabled"] = enabled
    return store[jid]


def trigger_job(jid: str):
    if jid not in store:
        return None
    return {"triggered": True, "job": store[jid]}
