import os
import logging

logger = logging.getLogger(__name__)


class ToolRegistry:
    def __init__(self):
        self.tools = {}

    def register(self, name, fn, description=""):
        self.tools[name] = {"fn": fn, "description": description}

    def call(self, name, args: dict):
        if name not in self.tools:
            raise ValueError(f"unknown tool {name}")
        return self.tools[name]["fn"](**args)

    def list_tools(self):
        return [{"name": k, "description": v["description"]} for k, v in self.tools.items()]


registry = ToolRegistry()


def calendar(user_id: str, date: str):
    google_key = os.getenv("GOOGLE_CALENDAR_API_KEY")
    if google_key:
        try:
            import httpx
            resp = httpx.get(
                "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                params={"key": google_key, "timeMin": f"{date}T00:00:00Z", "timeMax": f"{date}T23:59:59Z", "singleEvents": "true"},
                headers={"Authorization": f"Bearer {os.getenv('GOOGLE_CALENDAR_TOKEN', '')}"},
                timeout=10,
            )
            if resp.status_code == 200:
                items = resp.json().get("items", [])
                events = [{"title": e.get("summary", "untitled"), "date": e.get("start", {}).get("dateTime", date), "user_id": user_id} for e in items[:5]]
                return {"events": events, "source": "google"}
            logger.warning(f"Google Calendar API error: {resp.status_code}")
        except Exception as e:
            logger.warning(f"Google Calendar call failed: {e}")
    return {"events": [{"title": "mock meeting", "date": date, "user_id": user_id}], "source": "mock"}


def search(query: str):
    tavily_key = os.getenv("TAVILY_API_KEY")
    if tavily_key:
        try:
            import httpx
            resp = httpx.post(
                "https://api.tavily.com/search",
                json={"api_key": tavily_key, "query": query, "max_results": 3, "search_depth": "basic"},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for r in data.get("results", [])[:3]:
                    results.append({"title": r.get("title", ""), "url": r.get("url", ""), "snippet": r.get("content", "")[:200]})
                return {"results": results, "source": "tavily"}
            logger.warning(f"Tavily API error: {resp.status_code}")
        except Exception as e:
            logger.warning(f"Tavily search failed: {e}")
    serpapi_key = os.getenv("SERPAPI_KEY")
    if serpapi_key:
        try:
            import httpx
            resp = httpx.get(
                "https://serpapi.com/search",
                params={"api_key": serpapi_key, "q": query, "engine": "google", "num": 3},
                timeout=10,
            )
            if resp.status_code == 200:
                data = resp.json()
                results = []
                for r in data.get("organic_results", [])[:3]:
                    results.append({"title": r.get("title", ""), "url": r.get("link", ""), "snippet": r.get("snippet", "")[:200]})
                return {"results": results, "source": "serpapi"}
            logger.warning(f"SerpAPI error: {resp.status_code}")
        except Exception as e:
            logger.warning(f"SerpAPI search failed: {e}")
    return {"result": f"mock result for {query}", "source": "mock"}


def memo(user_id: str, content: str):
    try:
        from backend.app.api.chat import memory_service
        memory_service.write(user_id=user_id, content=content)
    except Exception:
        pass
    return {"ok": True, "content": content}


registry.register("calendar", calendar, "get calendar events for a date")
registry.register("search", search, "search the web (Tavily/SerpAPI)")
registry.register("memo", memo, "write memo to memory")
