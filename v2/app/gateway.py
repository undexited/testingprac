from time import perf_counter
import requests
from fastapi import HTTPException
from .config import get_settings


settings = get_settings()
_provider_stats: dict[str, dict[str, float]] = {
    "openai": {"avg_latency": 1800.0, "success_rate": 0.99},
    "anthropic": {"avg_latency": 2100.0, "success_rate": 0.99},
    "ollama": {"avg_latency": 1400.0, "success_rate": 0.99},
    "builtin": {"avg_latency": 250.0, "success_rate": 1.0},
}
_provider_cost: dict[str, float] = {
    "openai": 3.0,
    "anthropic": 3.5,
    "ollama": 0.2,
    "builtin": 0.0,
}


def _resolve_model(mode: str) -> str:
    return settings.think_model if mode == "think" else settings.fast_model


def _ollama_generate(model: str, prompt: str, system_prompt: str = "") -> str:
    try:
        resp = requests.post(
            f"{settings.ollama_base_url}/api/generate",
            json={"model": model, "prompt": prompt, "system": system_prompt, "stream": False},
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Ollama request failed: {exc}")


def _openai_generate(prompt: str, mode: str, system_prompt: str = "") -> str:
    if not settings.openai_api_key:
        raise HTTPException(status_code=400, detail="OPENAI_API_KEY not configured")
    model = settings.openai_model
    body = {
        "model": model,
        "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
        "temperature": 0.2 if mode == "fast" else 0.4,
    }
    headers = {"Authorization": f"Bearer {settings.openai_api_key}", "Content-Type": "application/json"}
    try:
        resp = requests.post("https://api.openai.com/v1/chat/completions", json=body, headers=headers, timeout=120)
        resp.raise_for_status()
        return resp.json()["choices"][0]["message"]["content"].strip()
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"OpenAI request failed: {exc}")


def _anthropic_generate(prompt: str, mode: str, system_prompt: str = "") -> str:
    if not settings.anthropic_api_key:
        raise HTTPException(status_code=400, detail="ANTHROPIC_API_KEY not configured")
    body = {
        "model": settings.anthropic_model,
        "system": system_prompt,
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


def _provider_order(provider_override: str | None = None) -> list[str]:
    if provider_override:
        return [provider_override.lower()]

    configured = [p.strip().lower() for p in settings.default_provider.split(",") if p.strip()]
    if not configured:
        configured = ["openai", "anthropic", "builtin"]

    def score(p: str) -> float:
        stats = _provider_stats.get(p, {"avg_latency": 2000.0, "success_rate": 0.9})
        return (_provider_cost.get(p, 5.0) * 0.6) + (stats["avg_latency"] / 1000.0 * 0.3) + ((1 - stats["success_rate"]) * 10 * 0.1)

    return sorted(configured, key=score)


def _update_stats(provider: str, latency_ms: int, success: bool) -> None:
    stats = _provider_stats.setdefault(provider, {"avg_latency": float(latency_ms), "success_rate": 1.0})
    stats["avg_latency"] = (stats["avg_latency"] * 0.8) + (latency_ms * 0.2)
    stats["success_rate"] = (stats["success_rate"] * 0.9) + ((1.0 if success else 0.0) * 0.1)


def _builtin_generate(prompt: str, mode: str, system_prompt: str = "") -> str:
    trimmed = prompt.strip()
    if mode == "think":
        return (
            "Analysis:\n"
            f"- Intent: {trimmed[:220]}\n"
            "- Key constraints: clarify objectives, constraints, and success criteria.\n"
            "- Risks: hidden assumptions, missing context, and implementation edge cases.\n\n"
            "Recommended next step:\n"
            "- I can turn this into an execution plan and then implement the first step."
        )
    if system_prompt:
        return f"{system_prompt}\n\nResponse:\n{trimmed[:500]}"
    return f"{trimmed[:700]}"


def generate_response(
    prompt: str,
    mode: str,
    provider_override: str | None = None,
    system_prompt: str = "",
) -> tuple[str, str, str, int]:
    started = perf_counter()
    errors: list[str] = []
    providers = _provider_order(provider_override)

    for provider in providers:
        try:
            if provider == "openai":
                model = settings.openai_model
                text = _openai_generate(prompt, mode, system_prompt)
            elif provider == "anthropic":
                model = settings.anthropic_model
                text = _anthropic_generate(prompt, mode, system_prompt)
            elif provider == "ollama":
                model = _resolve_model(mode)
                text = _ollama_generate(model, prompt, system_prompt)
            elif provider == "builtin":
                model = "builtin-think-v1" if mode == "think" else "builtin-fast-v1"
                text = _builtin_generate(prompt, mode, system_prompt)
            else:
                raise HTTPException(status_code=400, detail=f"Unsupported provider: {provider}")

            latency_ms = int((perf_counter() - started) * 1000)
            _update_stats(provider, latency_ms, True)
            return text, model, provider, latency_ms
        except Exception as exc:
            if isinstance(exc, HTTPException):
                errors.append(f"{provider}: {exc.detail}")
            else:
                errors.append(f"{provider}: {exc}")
            latency_ms = int((perf_counter() - started) * 1000)
            _update_stats(provider, latency_ms, False)
            continue

    raise HTTPException(status_code=502, detail=f"All providers failed. {errors}")
