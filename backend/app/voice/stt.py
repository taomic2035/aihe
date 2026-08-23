import os
import time


class STTService:
    def __init__(self, provider: str | None = None):
        env_provider = os.getenv("STT_PROVIDER", os.getenv("VOICE_PROVIDER", "mock"))
        self.provider = provider or env_provider
        if self.provider == "deepgram" and not os.getenv("DEEPGRAM_API_KEY"):
            self.provider = "mock"
        self._client = None
        self._sensevoice = None
        if self.provider == "deepgram":
            try:
                from deepgram import DeepgramClient
                self._client = DeepgramClient(os.getenv("DEEPGRAM_API_KEY"))
            except Exception:
                self.provider = "mock"
        if self.provider == "sensevoice":
            try:
                from funasr import AutoModel
                model_dir = os.path.expanduser("~/.cache/modelscope/hub/models/iic/SenseVoiceSmall")
                self._sensevoice = AutoModel(model=model_dir, trust_remote_code=True)
            except Exception as e:
                print(f"sensevoice init fail: {e}, falling back to mock")
                self.provider = "mock"

    def transcribe(self, audio: bytes) -> str:
        if self.provider == "mock":
            time.sleep(0.03)
            return "你好"
        if self.provider == "sensevoice":
            return self._sensevoice_transcribe(audio)
        try:
            result = self._client.listen.v("1").transcribe_file({"buffer": audio}, {"model": "nova-3"})
            return result["results"]["channels"][0]["alternatives"][0]["transcript"] or "你好"
        except Exception:
            time.sleep(0.03)
            return "你好"

    def _sensevoice_transcribe(self, audio: bytes) -> str:
        import tempfile
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio)
            tmp_path = f.name
        try:
            res = self._sensevoice.generate(input=tmp_path, language="auto", use_itn=True)
            if res and res[0].get("text"):
                return res[0]["text"]
            return "你好"
        except Exception as e:
            print(f"sensevoice transcribe fail: {e}")
            return "你好"
        finally:
            os.unlink(tmp_path)
