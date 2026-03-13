Backend README

Prereqs:
- Python 3.10+
- Ollama running locally (expected at http://localhost:11434)
- (Optional) LiveKit server if you want full voice room support

Install:
```
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Run:
```
uvicorn main:app --reload --port 8000
```

Notes:
- This example uses in-memory session storage (no DB).
- Whisper transcription requires the `whisper` package and model downloads.

Environment variables (optional):
- `LIVEKIT_URL`, `LIVEKIT_API_KEY`, `LIVEKIT_API_SECRET` (if you want tokens). When set, `/start-session` will return a `livekit` object with `url`, `api_key` and `token`.

Example (Windows PowerShell):
```
$env:LIVEKIT_URL = "wss://vox-test-f8szx891.livekit.cloud"
$env:LIVEKIT_API_KEY = "APIvyggry7rEnq8"
$env:LIVEKIT_API_SECRET = "erz0bENuBobTSC9sOy7esC4OZeHcqInYpM5NqW2oWg0B"
uvicorn main:app --reload --port 8000
```
