"""
Simple wrapper around OpenAI's whisper package for local transcription.
Accepts raw audio bytes (wav/webm). This file keeps logic minimal.
"""
import os
import tempfile

try:
    import whisper
except Exception:
    whisper = None

# Cache the model at module level so it's loaded only once
_model = None


def _get_model(model_name: str = "base"):
    global _model
    if _model is None and whisper is not None:
        _model = whisper.load_model(model_name)
    return _model


def transcribe_audio_bytes(audio_bytes: bytes, model_name: str = "base") -> str:
    """
    Transcribe raw audio bytes using a local Whisper model.

    Args:
        audio_bytes: Raw audio file content (wav, webm, etc.)
        model_name: Whisper model size (tiny, base, small, medium, large)

    Returns:
        Transcribed text string, or an error message if Whisper is unavailable.
    """
    if whisper is None:
        return "[Whisper not installed — install openai-whisper package to enable STT]"

    model = _get_model(model_name)

    # Write bytes to a temp file. Use delete=False on Windows to avoid
    # file-locking issues — Whisper needs to read the file while it exists.
    tmp = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    try:
        tmp.write(audio_bytes)
        tmp.flush()
        tmp.close()  # Close before Whisper reads on Windows
        res = model.transcribe(tmp.name)
        return res.get("text", "")
    except Exception as e:
        return f"[Whisper transcription error: {e}]"
    finally:
        try:
            os.unlink(tmp.name)
        except OSError:
            pass
