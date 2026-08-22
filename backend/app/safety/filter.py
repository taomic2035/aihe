CRISIS = {
    "resource": "ThroughLine 危机资源: 可拨打 988 或访问 https://findahelpline.org/ （1500+ 服务/170 国家）",
    "action": "pause",
}


def check(text: str) -> dict:
    high_keywords = ["不想活了", "自杀", "想死", "自残", "活不下去"]
    for kw in high_keywords:
        if kw in text:
            return {"risk": "high", "crisis": CRISIS["resource"], "action": "pause"}
    return {"risk": "low", "crisis": None, "action": "allow"}
