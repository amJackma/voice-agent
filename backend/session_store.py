"""
Simple in-memory session store. Each session holds uploads (bytes) and metadata.
No persistence; for demo only.
"""
from typing import Optional
from uuid import uuid4
from datetime import datetime

_SESSIONS: dict = {}

def create_session(name: str, designation: str, resume_bytes: bytes, jd_bytes: Optional[bytes], mode: str) -> str:
    session_id = str(uuid4())
    _SESSIONS[session_id] = {
        "id": session_id,
        "name": name,
        "designation": designation,
        "resume": resume_bytes,
        "jd": jd_bytes,
        "mode": mode,
        "created_at": datetime.utcnow().isoformat(),
        "history": [],
        "answers": [],
    }
    return session_id

def get_session(session_id: str) -> Optional[dict]:
    return _SESSIONS.get(session_id)

def append_history(session_id: str, role: str, text: str):
    s = _SESSIONS.get(session_id)
    if not s:
        return
    s["history"].append({"role": role, "text": text, "ts": datetime.utcnow().isoformat()})

def add_answer(session_id: str, question: str, answer: str):
    s = _SESSIONS.get(session_id)
    if not s:
        return
    s["answers"].append({"question": question, "answer": answer})
