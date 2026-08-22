def test_voice_provider_flag_downgrade():
    import os

    os.environ["VOICE_PROVIDER"] = "mock"
    from backend.app.voice.stt import STTService
    from backend.app.voice.tts import TTSService

    stt = STTService(provider="mock")
    assert stt.transcribe(b"fake") == "你好"
    tts = TTSService(provider="mock")
    assert len(tts.synthesize("hi")) > 0


def test_voice_real_fallback_when_no_key():
    import os

    os.environ["VOICE_PROVIDER"] = "deepgram"
    os.environ.pop("DEEPGRAM_API_KEY", None)
    from backend.app.voice.stt import STTService

    stt = STTService(provider="deepgram")
    # without key should fallback to mock, not raise
    text = stt.transcribe(b"fake")
    assert isinstance(text, str)


def test_voice_pipeline_with_flag():
    import os

    os.environ["VOICE_PROVIDER"] = "mock"
    from backend.app.voice.pipeline import VoicePipeline

    pipe = VoicePipeline()
    out = pipe.voice_to_voice(b"audio")
    assert len(out) > 0
