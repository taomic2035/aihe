import os
import time
from typing import Any

_traces: list[dict[str, Any]] = []
_real_client = None
_real_available = False

try:
    if os.getenv("LANGFUSE_HOST"):
        from langfuse import Langfuse

        _real_client = Langfuse(
            host=os.getenv("LANGFUSE_HOST"),
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY", ""),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY", ""),
        )
        _real_available = True
except Exception:
    _real_client = None


def trace(name: str, **kwargs):
    def decorator(fn):
        def wrapper(*args, **kw):
            t0 = time.perf_counter()
            if _real_client:
                try:
                    t = _real_client.trace(name=name, metadata=kwargs)
                    span = t.span(name=f"{name}.exec")
                    result = fn(*args, **kw)
                    span.end()
                    _traces.append({"name": name, "duration_ms": (time.perf_counter() - t0) * 1000, "real": True})
                    return result
                except Exception:
                    pass
            result = fn(*args, **kw)
            _traces.append({"name": name, "duration_ms": (time.perf_counter() - t0) * 1000, "args": args, "kwargs": kwargs, "meta": kw, "real": False})
            return result

        return wrapper

    return decorator


def log_trace(name: str, data: dict):
    _traces.append({"name": name, "data": data, "real": bool(_real_client)})
    if _real_client:
        try:
            _real_client.trace(name=name, metadata=data)
        except Exception:
            pass


def log_generation(name: str, input_data: dict, output_data: dict, model: str = "", duration_ms: float = 0):
    _traces.append({"name": name, "type": "generation", "input": input_data, "output": output_data, "model": model, "duration_ms": duration_ms})
    if _real_client:
        try:
            t = _real_client.trace(name=name)
            t.generation(name=name, input=input_data, output=output_data, model=model, start_time=time.time(), end_time=time.time() + duration_ms / 1000)
        except Exception:
            pass


def get_traces() -> list[dict]:
    return list(_traces)


def clear_traces():
    _traces.clear()


def is_real() -> bool:
    return _real_available


def flush():
    if _real_client:
        try:
            _real_client.flush()
        except Exception:
            pass
