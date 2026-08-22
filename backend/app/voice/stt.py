import time


class STTService:
    def __init__(self, provider: str = "mock"):
        self.provider = provider

    def transcribe(self, audio: bytes) -> str:
        if self.provider == "mock":
            # fake latency 30ms
            time.sleep(0.03)
            return "你好"
        # real Deepgram path deferred
        raise NotImplementedError
