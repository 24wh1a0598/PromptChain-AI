"""
LLM wrapper — calls OpenRouter API.
"""
import os
import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env", override=False)
load_dotenv(dotenv_path=".env.example", override=False)

API_KEY = os.getenv("OPENROUTER_API_KEY")
if not API_KEY:
    raise ValueError("OPENROUTER_API_KEY not found in .env or .env.example")

API_URL = "https://openrouter.ai/api/v1/chat/completions"
DEFAULT_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
FALLBACK_MODEL = "openai/gpt-4o-mini"
DEFAULT_MAX_TOKENS = int(os.getenv("OPENROUTER_MAX_TOKENS", "600"))


def call_llm(
    system_prompt: str,
    user_prompt: str,
    model: str | None = None,
    max_tokens: int | None = None,
) -> str:
    """
    Calls the OpenRouter API with a system + user prompt.
    Returns the assistant's reply text.
    """
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json",
    }

    effective_model = model or DEFAULT_MODEL
    effective_max_tokens = max_tokens if max_tokens is not None else DEFAULT_MAX_TOKENS

    payload = {
        "model": effective_model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": 0.0,  # deterministic for JSON
        "max_tokens": effective_max_tokens,
    }

    try:
        response = requests.post(
            API_URL,
            headers=headers,
            json=payload,
            timeout=60,
        )
        response.raise_for_status()
    except requests.HTTPError as exc:
        if exc.response is not None and exc.response.status_code in {402, 429} and effective_model != FALLBACK_MODEL:
            payload["model"] = FALLBACK_MODEL
            response = requests.post(
                API_URL,
                headers=headers,
                json=payload,
                timeout=60,
            )
            response.raise_for_status()
        else:
            raise

    return response.json()["choices"][0]["message"]["content"]