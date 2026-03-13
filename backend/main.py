"""
FastAPI backend implementing simple endpoints for session start, STT, ask (LLM-driven Q/A), and scoring.
Files:
- `session_store.py` - in-memory store
- `ollama_client.py` - minimal HTTP client to local Ollama
- `whisper_stt.py` - wrapper to local Whisper
- `prompts.py` - prompt templates

This keeps things minimal and focused on clarity.
"""
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os
import json
from typing import Optional

from session_store import create_session, get_session, append_history, add_answer
from ollama_client import ask_ollama
from whisper_stt import transcribe_audio_bytes
from prompts import build_question_prompt, build_score_prompt
from livekit_token import create_access_token

# Load LiveKit config from environment if available
LIVEKIT_URL = os.environ.get("LIVEKIT_URL")
LIVEKIT_API_KEY = os.environ.get("LIVEKIT_API_KEY")
LIVEKIT_API_SECRET = os.environ.get("LIVEKIT_API_SECRET")


OLLAMA_MODEL = "llama3"

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/start-session")
async def start_session(
    name: str = Form(...),
    designation: str = Form(...),
    mode: str = Form(...),
    resume: UploadFile = File(...),
    jd: Optional[UploadFile] = None,
):
    resume_bytes = await resume.read()
    jd_bytes = await jd.read() if jd is not None else None
    session_id = create_session(name, designation, resume_bytes, jd_bytes, mode)

    room_name = f"jhex-room-{session_id}"
    result = {"session_id": session_id, "room": room_name}

    if LIVEKIT_API_KEY and LIVEKIT_API_SECRET:
        identity = name
        token = create_access_token(
            LIVEKIT_API_KEY,
            LIVEKIT_API_SECRET,
            identity=identity,
            room=room_name
        )
        result.update({
            "livekit": {
                "url": LIVEKIT_URL,
                "api_key": LIVEKIT_API_KEY,
                "token": token
            }
        })
    return result


@app.get("/session/{session_id}")
def read_session(session_id: str):
    s = get_session(session_id)
    if not s:
        return JSONResponse({"error": "not found"}, status_code=404)

    return {
        "id": s["id"],
        "name": s["name"],
        "designation": s["designation"],
        "has_jd": bool(s.get("jd")),
        "history": s["history"],
    }


@app.post("/stt")
async def stt(audio: UploadFile = File(...)):
    audio_bytes = await audio.read()
    text = transcribe_audio_bytes(audio_bytes)
    return {"text": text}


@app.post("/ask")
async def ask(session_id: str = Form(...), user_text: Optional[str] = Form(None)):
    s = get_session(session_id)
    if not s:
        return JSONResponse({"error": "session not found"}, status_code=404)

    if user_text:
        append_history(session_id, "user", user_text)

    prompt = build_question_prompt(s, last_user_answer=user_text)

    agent_text = ask_ollama(OLLAMA_MODEL, prompt)

    append_history(session_id, "agent", agent_text)

    if user_text:
        add_answer(session_id, question=agent_text, answer=user_text)

    return {"agent": agent_text}


@app.post("/score")
async def score(session_id: str = Form(...)):
    s = get_session(session_id)
    if not s:
        return JSONResponse({"error": "session not found"}, status_code=404)

    prompt = build_score_prompt(s)
    answers_text = "\n".join(
        [f"Q: {a['question']} A: {a['answer']}" for a in s.get("answers", [])]
    )
    full_prompt = prompt + "\nCandidate answers:\n" + answers_text

    res = ask_ollama(OLLAMA_MODEL, full_prompt)


    try:
        parsed = json.loads(res)
    except Exception:
        parsed = {"raw": res}

    return {"result": parsed}
