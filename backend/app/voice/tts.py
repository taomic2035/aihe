import os
import time


class TTSService:
    def __init__(self, provider: str | None = None):
        env_provider = os.getenv("VOICE_PROVIDER", "mock")
        # support fish|elevenlabs|cosyvoice|mock
        self.provider = provider or env_provider
        if self.provider in ("fish", "elevenlabs", "fish-audio") and not os.getenv("FISH_API_KEY") and not os.getenv("ELEVENLABS_API_KEY"):
            # no key -> fallback
            self.provider = "mock"
        if self.provider == "cosyvoice" and not os.getenv("COSYVOICE_URL"):
            self.provider = "mock"
        self._client = None

    def synthesize(self, text: str, emotion: str = "warm") -> bytes:
        if self.provider == "mock":
            time.sleep(0.03)
            return f"fake-audio-{text}-{emotion}".encode()
        # real paths with fallback
        try:
            if self.provider in ("fish", "fish-audio"):
                # Fish Audio real SDK placeholder: http call
                import httpx

                resp = httpx.post(
                    os.getenv("FISH_API_URL", "https://api.fish.audio/v1/tts"),
                    headers={"Authorization": f"Bearer {os.getenv('FISH_API_KEY')}"},
                    json={"text": text, "emotion": emotion},
                    timeout=5,
                )
                if resp.status_code == 200:
                    return resp.content
                raise RuntimeError("fish tts failed")
            elif self.provider == "elevenlabs":
                import httpx

                voice_id = os.getenv("ELEVENLABS_VOICE_ID", "EXAVITQu4vr4xnSDxMaL")
                resp = httpx.post(
                    f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                    headers={"xi-api-key": os.getenv("ELEVENLABS_API_KEY")},
                    json={"text": text, "model_id": "eleven_turbo_v2_5"},
                    timeout=10,
                )
                if resp.status_code == 200:
                    return resp.content
                raise RuntimeError("elevenlabs failed")
        except Exception:
            pass
        # fallback
        time.sleep(0.03)
        return f"fake-audio-{text}-{emotion}-fallback".encode()
