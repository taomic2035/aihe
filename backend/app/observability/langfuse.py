import os
from typing import Any

# Minimal mock Langfuse tracer — real SDK when LANGFUSE_HOST set
_traces: list[dict[str, Any]] = []
_real_client = None
try:
    if os.getenv("LANGFUSE_HOST"):
        from langfuse import Langfuse  # type: ignore

        _real_client = Langfuse(
            host=os.getenv("LANGFUSE_HOST"),
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY", ""),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY", ""),
        )
except Exception:
    _real_client = None


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
    if _real_client:
        try:
            _real_client.trace(name=name, metadata=data)
        except Exception:
            pass


def get_traces() -> list[dict]:
    return list(_traces)


def clear_traces():
    _traces.clear()
