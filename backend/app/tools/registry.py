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
    return {"events": [{"title": "mock meeting", "date": date, "user_id": user_id}]}


def search(query: str):
    return {"result": f"mock result for {query}"}


def memo(user_id: str, content: str):
    # write to memory
    try:
        from backend.app.api.chat import memory_service

        memory_service.write(user_id=user_id, content=content)
    except Exception:
        pass
    return {"ok": True, "content": content}


registry.register("calendar", calendar, "get calendar events")
registry.register("search", search, "search web")
registry.register("memo", memo, "write memo to memory")
