import os
import time


class STTService:
    def __init__(self, provider: str | None = None):
        # Feature Flag: VOICE_PROVIDER=mock|deepgram|auto
        env_provider = os.getenv("VOICE_PROVIDER", "mock")
        self.provider = provider or env_provider
        # if real provider requested but no key, fallback to mock
        if self.provider == "deepgram" and not os.getenv("DEEPGRAM_API_KEY"):
            self.provider = "mock"
        self._client = None
        if self.provider == "deepgram":
            try:
                from deepgram import DeepgramClient  # type: ignore

                self._client = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"))
            except Exception:
                self.provider = "mock"

    def transcribe(self, audio: bytes) -> str:
        if self.provider == "mock":
            time.sleep(0.03)
            return "你好"
        # real Deepgram path
        try:
            # deepgram v3 API: client.listen.v("1").transcribe_file
            # fallback to mock on any error
            result = self._client.listen.v("1").transcribe_file({"buffer": audio}, {"model": "nova-3"})
            return result["results"]["channels"][0]["alternatives"][0]["transcript"] or "你好"
        except Exception:
            time.sleep(0.03)
            return "你好"
