from time import perf_counter
import requests
from fastapi import HTTPException
from .config import get_settings


settings = get_settings()


def _resolve_model(mode: str) -> str:
    return settings.think_model if mode == "think" else settings.fast_model


def _ollama_generate(model: str, prompt: str) -> str:
    try:
        resp = requests.post(
            f"{settings.ollama_base_url}/api/generate",
            json={"model": model, "prompt": prompt, "stream": False},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Ollama request failed: {exc}")


def _openai_generate(prompt: str, mode: str) -> str:
    if not settings.openai_api_key:
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY not configured")
    model = settings.openai_model
    body = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2 if mode == "fast" else 0.4,
    }
    headers = {"Authorization": f"Bearer {settings.openai_api_key}", "Content-Type": "application/json"}
    try:
        resp = requests.post("https://api.openai.com/v1/chat/completions", json=body, headers=headers, timeout=120)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI request failed: {exc}")


def _anthropic_generate(prompt: str, mode: str) -> str:
    if not settings.anthropic_api_key:
        raise HTTPException(status_code=400, detail="ANTHROPIC_API_KEY not configured")
    body = {
        "model": settings.anthropic_model,
        "max_tokens": 350 if mode == "fast" else 900,
        "temperature": 0.2 if mode == "fast" else 0.5,
        "messages": [{"role": "user", "content": prompt}],
    }
    headers = {
        "x-api-key": settings.anthropic_api_key,
        "anthropic-version": "2023-06-01",
        "content-type": "application/json",
    }
    try:
        resp = requests.post("https://api.anthropic.com/v1/messages", json=body, headers=headers, timeout=120)
        resp.raise_for_status()
        chunks = resp.json().get("content", [])
        text = "".join(part.get("text", "") for part in chunks if part.get("type") == "text")
        return text.strip()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Anthropic request failed: {exc}")


def generate_response(prompt: str, mode: str, provider_override: str | None = None) -> tuple[str, str, int]:
    provider = (provider_override or settings.default_provider).lower()
    started = perf_counter()

    if provider == "ollama":
        model = _resolve_model(mode)
        text = _ollama_generate(model, prompt)
    elif provider == "openai":
        model = settings.openai_model
        text = _openai_generate(prompt, mode)
    elif provider == "anthropic":
        model = settings.anthropic_model
        text = _anthropic_generate(prompt, mode)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")

    latency_ms = int((perf_counter() - started) * 1000)
    return text, model, latency_ms
