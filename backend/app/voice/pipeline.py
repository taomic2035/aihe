from backend.app.voice.stt import STTService
from backend.app.voice.tts import TTSService


class VoicePipeline:
    def __init__(self, stt: STTService | None = None, tts: TTSService | None = None):
        self.stt = stt or STTService(provider="mock")
        self.tts = tts or TTSService(provider="mock")

    def voice_to_voice(self, audio: bytes, emotion: str = "warm") -> bytes:
        text = self.stt.transcribe(audio)
        return self.tts.synthesize(text, emotion=emotion)

    def voice_to_text(self, audio: bytes) -> str:
        return self.stt.transcribe(audio)

    def text_to_voice(self, text: str, emotion: str = "warm") -> bytes:
        return self.tts.synthesize(text, emotion=emotion)
