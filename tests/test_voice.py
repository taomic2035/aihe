def test_stt_tts_mock():
    from backend.app.voice.stt import STTService
    from backend.app.voice.tts import TTSService

    stt = STTService(provider="mock")
    assert stt.transcribe(b"fake audio") == "你好"
    tts = TTSService(provider="mock")
    audio = tts.synthesize("你好", emotion="warm")
    assert len(audio) > 0
    assert b"warm" in audio or b"fake-audio" in audio


def test_voice_pipeline():
    from backend.app.voice.stt import STTService
    from backend.app.voice.tts import TTSService
    from backend.app.voice.pipeline import VoicePipeline

    stt = STTService(provider="mock")
    tts = TTSService(provider="mock")
    pipe = VoicePipeline(stt=stt, tts=tts)
    out = pipe.voice_to_voice(b"audio")
    assert len(out) > 0
