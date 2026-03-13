"""
Prompt templates used to ask the LLM (Ollama) to act as an interviewer.
Keep templates short and clear.

Uses PyPDF2 to extract text from uploaded PDF bytes so the LLM gets
actual resume/JD content instead of placeholder strings.
"""
from typing import Optional

try:
    from PyPDF2 import PdfReader
    import io
except ImportError:
    PdfReader = None

BASE_SYSTEM = (
    "You are a professional technical interviewer. Ask concise, relevant interview questions "
    "one at a time. Use the job description if available; otherwise use the candidate resume and role."
)


def _extract_pdf_text(pdf_bytes: Optional[bytes], max_chars: int = 3000) -> str:
    """Extract text from PDF bytes. Returns empty string on failure."""
    if not pdf_bytes or PdfReader is None:
        return ""
    try:
        reader = PdfReader(io.BytesIO(pdf_bytes))
        text = ""
        for page in reader.pages:
            text += (page.extract_text() or "")
            if len(text) >= max_chars:
                break
        return text[:max_chars].strip()
    except Exception:
        return ""


def build_question_prompt(session: dict, last_user_answer: Optional[str] = None) -> str:
    role = session.get("designation", "")
    mode = session.get("mode", "Mock Interview")

    # Extract actual content from uploaded PDFs
    resume_text = _extract_pdf_text(session.get("resume"))
    jd_text = _extract_pdf_text(session.get("jd"))

    context = f"{BASE_SYSTEM}\nRole: {role}\nSession mode: {mode}\n"

    if jd_text:
        context += f"Job Description:\n{jd_text}\n"
    else:
        context += "No job description provided. Use the resume and role standards.\n"

    if resume_text:
        context += f"Candidate Resume:\n{resume_text}\n"
    else:
        context += "Resume text could not be extracted.\n"

    # Include conversation history for continuity
    history = session.get("history", [])
    if history:
        context += "\nConversation so far:\n"
        for entry in history[-6:]:  # last 6 turns for context window
            context += f"  {entry['role']}: {entry['text']}\n"

    if last_user_answer:
        context += f"\nLast user answer: {last_user_answer}\n"

    # Ask the model to produce one question
    prompt = context + (
        "\nGenerate one interview question appropriate for the candidate. "
        "If the answer would likely be shallow, include a brief follow-up prompt. "
        "Return only the question and optional follow-up in plain text."
    )
    return prompt


def build_score_prompt(session: dict) -> str:
    role = session.get("designation", "")
    jd_text = _extract_pdf_text(session.get("jd"))

    prompt = (
        "You are an interviewer evaluating the candidate from the session. "
        f"Role: {role}. "
    )
    if jd_text:
        prompt += f"Job Description context: {jd_text[:1500]}\n"

    prompt += (
        "Given the candidate's answers (list) and role, provide: a numeric score out of 100, "
        "3 strengths (bulleted), 2 weak areas (bulleted), and Hiring Recommendation (Yes/Maybe/No). "
        "Base evaluation on depth, system thinking and relevance to job description if present. "
        "Return JSON with keys: score, strengths, weaknesses, recommendation."
    )
    return prompt
