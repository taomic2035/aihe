import re
import time
import asyncio
import logging
from fastapi import APIRouter, UploadFile, File, Form, Request
from fastapi.responses import Response, StreamingResponse
from pydantic import BaseModel
from backend.app.voice.stt import STTService
from backend.app.voice.tts import TTSService
from backend.app.voice.pipeline import VoicePipeline
from backend.app.api.chat import memory_service, persona_service, llm_router
from backend.app.realtime.manager import manager

logger = logging.getLogger(__name__)

router = APIRouter()

stt_service = STTService()
tts_service = TTSService()
pipeline = VoicePipeline(stt=stt_service, tts=tts_service)

_cancel_events: dict[str, asyncio.Event] = {}


def _sentence_split(text: str) -> list[str]:
    parts = re.split(r'(?<=[。！？；\n])', text)
    sentences = []
    buf = ""
    for p in parts:
        buf += p
        if len(buf) >= 8 and re.search(r'[。！？；\n]$', buf):
            sentences.append(buf.strip())
            buf = ""
    if buf.strip():
        sentences.append(buf.strip())
    return sentences if sentences else [text]


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
    ctype = "audio/wav" if audio[:4] == b"RIFF" else "audio/mpeg"
    return Response(content=audio, media_type=ctype)


class VoiceSessionRequest(BaseModel):
    user_id: str


@router.post("/v1/voice/session")
def voice_session(req: VoiceSessionRequest):
    return {"room": f"aihe-{req.user_id}", "token": "mock-token-aihe"}


@router.post("/v1/voice/barge-in")
async def voice_barge_in(user_id: str):
    evt = _cancel_events.get(user_id)
    if evt:
        evt.set()
        return {"status": "cancelled"}
    return {"status": "no_active_session"}


@router.post("/v1/voice/chat")
async def voice_chat(audio: UploadFile = File(None), user_id: str = Form(None), text: str = Form(None)):
    if text is None and audio is not None:
        data = await audio.read()
        text = stt_service.transcribe(data)
    if not text:
        text = "你好"
    if not user_id:
        user_id = "anonymous"

    cancel_event = asyncio.Event()
    _cancel_events[user_id] = cancel_event

    try:
        hits = memory_service.recall(user_id=user_id, query=text, limit=8)
        mems = [h.content for h in hits]
        persona = persona_service.build_system_prompt(user_id=user_id)

        full_reply = ""
        sentence_buf = ""

        def generate_streaming():
            nonlocal full_reply, sentence_buf
            for chunk in llm_router.stream(user_id=user_id, message=text, persona_prompt=persona, memories=mems):
                if cancel_event.is_set():
                    logger.info(f"barge-in cancelled for {user_id}")
                    return
                full_reply += chunk
                sentence_buf += chunk
                sentences = _sentence_split(sentence_buf)
                if len(sentences) > 1:
                    for s in sentences[:-1]:
                        if s:
                            audio_chunk = tts_service.synthesize(s, emotion="warm")
                            yield audio_chunk
                    sentence_buf = sentences[-1]

            if sentence_buf.strip():
                audio_chunk = tts_service.synthesize(sentence_buf.strip(), emotion="warm")
                yield audio_chunk

            if any(kw in text for kw in ["我叫", "喜欢", "住在"]):
                memory_service.write(user_id=user_id, content=text)

        audio_parts = list(generate_streaming())
        audio_out = b"".join(audio_parts)

        try:
            await manager.broadcast(user_id, full_reply)
        except Exception:
            pass

        ctype = "audio/wav" if audio_out[:4] == b"RIFF" else "audio/mpeg"
        return Response(content=audio_out, media_type=ctype)
    finally:
        _cancel_events.pop(user_id, None)


@router.post("/v1/voice/chat/stream")
async def voice_chat_stream(request: Request, audio: UploadFile = File(None), user_id: str = Form(None), text: str = Form(None)):
    if text is None and audio is not None:
        data = await audio.read()
        text = stt_service.transcribe(data)
    if not text:
        text = "你好"
    if not user_id:
        user_id = "anonymous"

    cancel_event = asyncio.Event()
    _cancel_events[user_id] = cancel_event

    hits = memory_service.recall(user_id=user_id, query=text, limit=8)
    mems = [h.content for h in hits]
    persona = persona_service.build_system_prompt(user_id=user_id)

    async def stream_audio():
        full_reply = ""
        sentence_buf = ""
        try:
            for chunk in llm_router.stream(user_id=user_id, message=text, persona_prompt=persona, memories=mems):
                if cancel_event.is_set():
                    break
                full_reply += chunk
                sentence_buf += chunk
                sentences = _sentence_split(sentence_buf)
                if len(sentences) > 1:
                    for s in sentences[:-1]:
                        if s:
                            audio_chunk = await tts_service.synthesize_async(s, emotion="warm")
                            yield audio_chunk
                    sentence_buf = sentences[-1]

            if sentence_buf.strip():
                audio_chunk = await tts_service.synthesize_async(sentence_buf.strip(), emotion="warm")
                yield audio_chunk

            if any(kw in text for kw in ["我叫", "喜欢", "住在"]):
                memory_service.write(user_id=user_id, content=text)

            try:
                await manager.broadcast(user_id, full_reply)
            except Exception:
                pass
        finally:
            _cancel_events.pop(user_id, None)

    return StreamingResponse(stream_audio(), media_type="audio/mpeg")


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
