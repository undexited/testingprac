# TestingPrac AI v2

`v2` is the first-party product path (not Open WebUI):

- Multi-user auth with admin visibility (`register/login/JWT`, login event feed)
- Organizations/workspaces/memberships
- Agent modes (`general`, `coder`, `analyst`) and `fast`/`think`
- Provider gateway with fallback (`openai`, `anthropic`, `builtin`, optional `ollama`)
- Desktop client with:
  - Chat tab
  - Agent tab
  - Code Studio (open/save/run snippets + coder analysis)
  - Admin tab (login events)

## Run backend locally

1. Configure provider keys in `.env` if using hosted models.
2. From repo root:

```powershell
powershell -ExecutionPolicy Bypass -File .\v2\run.ps1
```

API/Web endpoint:
- `http://127.0.0.1:8090`

## Run desktop app (no PowerShell/CMD window)

1. Launch directly:

```powershell
wscript.exe "C:\Users\helme\OneDrive\Documents\codexplay\v2\launch_desktop.vbs"
```

2. Optional desktop shortcut:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup\create-v2-desktop-shortcut.ps1
```

## Environment

Copy:

- `v2/.env.example` -> `v2/.env`

Then customize provider keys/models and `DEFAULT_PROVIDER` order.

## API overview (core)

- `POST /api/auth/register`
- `POST /api/auth/login`
- `GET /api/me`
- `GET /api/workspaces`
- `GET /api/agents`
- `GET /api/admin/login-events` (admin only)
- `GET /api/conversations`
- `GET /api/conversations/{id}/messages`
- `POST /api/chat/send`
