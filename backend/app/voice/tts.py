import time


class TTSService:
    def __init__(self, provider: str = "mock"):
        self.provider = provider

    def synthesize(self, text: str, emotion: str = "warm") -> bytes:
        if self.provider == "mock":
            time.sleep(0.03)
            return f"fake-audio-{text}-{emotion}".encode()
        raise NotImplementedError
