# TestingPrac AI v2.0

`v2` is a real multi-user chat platform scaffold (not Open WebUI) with:

- Account auth (register/login/JWT)
- Per-user conversations + messages
- Provider gateway routing:
  - `ollama`
  - `openai` (optional key)
  - `anthropic` (optional key)
- Mode-aware model routing (`fast` / `think`)
- Clean ChatGPT-style web app at `/`

## Run locally

1. Ensure Ollama is up if using default provider.
2. From repo root:

```powershell
powershell -ExecutionPolicy Bypass -File .\v2\run.ps1
```

Open:

- `http://127.0.0.1:8090`

## Environment

Copy:

- `v2/.env.example` -> `v2/.env`

Then customize provider keys/models.

## API overview

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/me`
- `GET /api/conversations`
- `GET /api/conversations/{id}/messages`
- `POST /api/chat/send`
