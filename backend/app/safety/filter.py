import re

CRISIS_RESOURCE = "ThroughLine 危机资源: 可拨打 988 或访问 https://findahelpline.org/ （1500+ 服务/170 国家）"

_HIGH_PATTERNS = [
    r"不想活", r"自杀", r"想死", r"自残", r"活不下去",
    r"结束生命", r"了结", r"跳楼", r"割腕", r"吞药",
    r"kill\s*myself", r"suicide", r"end\s*my\s*life", r"don'?t\s*want\s*to\s*live",
    r"self\s*harm", r"overdose",
]

_HIGH_RE = re.compile("|".join(_HIGH_PATTERNS), re.IGNORECASE)


def check(text: str) -> dict:
    if _HIGH_RE.search(text):
        return {"risk": "high", "crisis": CRISIS_RESOURCE, "action": "pause"}
    medium_kws = ["焦虑", "抑郁", "失眠", "崩溃", "撑不住", "depress", "anxious", "insomnia"]
    for kw in medium_kws:
        if kw in text.lower():
            return {"risk": "medium", "crisis": None, "action": "allow_with_care"}
    return {"risk": "low", "crisis": None, "action": "allow"}
