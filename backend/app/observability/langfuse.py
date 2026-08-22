from typing import Any

# Minimal mock Langfuse tracer for TDD; real langfuse SDK deferred to prod
_traces: list[dict[str, Any]] = []


def trace(name: str, **kwargs):
    def decorator(fn):
        def wrapper(*args, **kw):
            result = fn(*args, **kw)
            _traces.append({"name": name, "args": args, "kwargs": kwargs, "meta": kw})
            return result

        return wrapper

    return decorator


def log_trace(name: str, data: dict):
    _traces.append({"name": name, "data": data})


def get_traces() -> list[dict]:
    return list(_traces)


def clear_traces():
    _traces.clear()
