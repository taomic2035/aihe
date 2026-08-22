from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import Response
from pydantic import BaseModel
from backend.app.voice.stt import STTService
from backend.app.voice.tts import TTSService
from backend.app.voice.pipeline import VoicePipeline
from backend.app.api.chat import memory_service, persona_service, llm_router
from backend.app.realtime.manager import manager

router = APIRouter()

stt_service = STTService(provider="mock")
tts_service = TTSService(provider="mock")
pipeline = VoicePipeline(stt=stt_service, tts=tts_service)


@router.post("/v1/voice/stt")
async def voice_stt(audio: UploadFile = File(...)):
    data = await audio.read()
    text = stt_service.transcribe(data)
    return {"text": text}


class TTSRequest(BaseModel):
    text: str
    emotion: str = "warm"


@router.post("/v1/voice/tts")
def voice_tts(req: TTSRequest):
    audio = tts_service.synthesize(req.text, emotion=req.emotion)
    return Response(content=audio, media_type="audio/mpeg")


class VoiceSessionRequest(BaseModel):
    user_id: str


@router.post("/v1/voice/session")
def voice_session(req: VoiceSessionRequest):
    return {"room": f"aihe-{req.user_id}", "token": "mock-token-aihe"}


@router.post("/v1/voice/chat")
async def voice_chat(audio: UploadFile = File(None), user_id: str = Form(None), text: str = Form(None)):
    # Support both multipart audio and json fallback
    if text is None and audio is not None:
        data = await audio.read()
        # barge-in check header would be in request.headers, mock no-op
        text = stt_service.transcribe(data)
    if not text:
        # try json body fallback handled by alternate route
        text = "你好"
    if not user_id:
        user_id = "anonymous"
    # recall + persona + llm like chat.py
    hits = memory_service.recall(user_id=user_id, query=text, limit=8)
    mems = [h.content for h in hits]
    persona = persona_service.build_system_prompt(user_id=user_id)
    chunks = list(llm_router.stream(user_id=user_id, message=text, persona_prompt=persona, memories=mems))
    reply = "".join(chunks)
    audio_out = tts_service.synthesize(reply, emotion="warm")
    # persist
    if any(kw in text for kw in ["我叫", "喜欢", "住在"]):
        memory_service.write(user_id=user_id, content=text)
    # broadcast
    try:
        import asyncio

        await manager.broadcast(user_id, reply)
    except Exception:
        pass
    return Response(content=audio_out, media_type="audio/mpeg")


# JSON fallback for test
class VoiceChatJson(BaseModel):
    user_id: str
    text: str


@router.post("/v1/voice/chat/json")
def voice_chat_json(req: VoiceChatJson):
    hits = memory_service.recall(user_id=req.user_id, query=req.text, limit=8)
    mems = [h.content for h in hits]
    persona = persona_service.build_system_prompt(user_id=req.user_id)
    chunks = list(llm_router.stream(user_id=req.user_id, message=req.text, persona_prompt=persona, memories=mems))
    reply = "".join(chunks)
    audio = tts_service.synthesize(reply, emotion="warm")
    return Response(content=audio, media_type="audio/mpeg")
