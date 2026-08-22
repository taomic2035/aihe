import os
import time
import pathlib
import wave
import io


class TTSService:
    def __init__(self, provider: str | None = None):
        env_provider = os.getenv("VOICE_PROVIDER", "mock")
        self.provider = provider or env_provider
        # fallback if no key
        if self.provider in ("fish", "elevenlabs", "fish-audio") and not os.getenv("FISH_API_KEY") and not os.getenv("ELEVENLABS_API_KEY"):
            self.provider = "mock"
        if self.provider == "cosyvoice" and not os.getenv("COSYVOICE_URL"):
            self.provider = "mock"
        # piper needs voice file, check exists
        if self.provider == "piper":
            zh_path = pathlib.Path("/tmp/piper_voices/zh_CN-huayan-medium.onnx")
            if not zh_path.exists():
                self.provider = "mock"
        self._piper_voice = None
        if self.provider == "piper":
            try:
                from piper import PiperVoice

                zh_path = pathlib.Path("/tmp/piper_voices/zh_CN-huayan-medium.onnx")
                self._piper_voice = PiperVoice.load(str(zh_path))
            except Exception:
                self.provider = "mock"

    def _piper_wav(self, text: str) -> bytes:
        # synthesize via piper and wrap as WAV bytes for browser
        chunks = list(self._piper_voice.synthesize(text))
        audio_bytes = b"".join(c.audio_int16_bytes for c in chunks)
        sr = self._piper_voice.config.sample_rate
        buf = io.BytesIO()
        with wave.open(buf, "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(sr)
            wav.writeframes(audio_bytes)
        return buf.getvalue()

    def synthesize(self, text: str, emotion: str = "warm") -> bytes:
        if self.provider == "mock":
            time.sleep(0.03)
            return f"fake-audio-{text}-{emotion}".encode()
        if self.provider == "piper":
            try:
                return self._piper_wav(text[:300])
            except Exception:
                time.sleep(0.03)
                return f"fake-audio-{text}-{emotion}-fallback".encode()
        # real cloud paths
        try:
            if self.provider in ("fish", "fish-audio"):
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
        time.sleep(0.03)
        return f"fake-audio-{text}-{emotion}-fallback".encode()
