"""
Minimal Ollama client helper.
Uses Ollama HTTP API at http://localhost:11434/api/generate
"""

import requests
import time

OLLAMA_URL = "http://localhost:11434"

# Longer timeout because the first request may need to load the model into memory
OLLAMA_TIMEOUT = 120
MAX_RETRIES = 2


def ask_ollama(model: str, prompt: str) -> str:
    """
    Send a prompt to a local Ollama model and return the generated text.
    Retries once on timeout since the first call may need to load the model.

    Args:
        model (str): Ollama model name (e.g. 'llama3', 'mistral')
        prompt (str): Prompt text to send to the model

    Returns:
        str: Model response text or error message
    """
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }

    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json=payload,
                timeout=OLLAMA_TIMEOUT
            )
            response.raise_for_status()
            data = response.json()
            return data.get("response", "").strip()

        except requests.exceptions.Timeout as e:
            last_error = e
            if attempt < MAX_RETRIES - 1:
                time.sleep(2)  # brief pause before retry
                continue
        except requests.exceptions.ConnectionError as e:
            return f"[Ollama not reachable — is it running? Error: {e}]"
        except requests.exceptions.RequestException as e:
            return f"[Ollama HTTP error: {e}]"
        except Exception as e:
            return f"[Ollama error: {e}]"

    return f"[Ollama timed out after {MAX_RETRIES} attempts. The model may still be loading — try again in a moment.]"
