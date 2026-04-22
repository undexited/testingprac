# TestingPrac AI Platform

Primary product direction is now `v2.0` in `v2/`: a multi-user chat platform (ChatGPT/Anthropic-style architecture) with provider routing and first-party desktop + web UI.

## v2.0 quick start

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\v2\run.ps1
```

Open:

- `http://127.0.0.1:8090`

Desktop app (hidden launch, no visible PowerShell/CMD):

```powershell
wscript.exe "C:\Users\helme\OneDrive\Documents\codexplay\v2\launch_desktop.vbs"
```

Details:

- `v2/README.md`

## v2.0 highlights

- Multi-user auth (register/login/JWT)
- Per-user chat history and conversations
- Provider gateway routing:
  - OpenAI
  - Anthropic
  - Builtin fallback (no external model dependency)
  - Optional Ollama
- Mode-based routing (`fast` / `think`)
- First-party desktop + web app (no Open WebUI dependency)

## Legacy stack (v0.x)

Older Open WebUI/Ollama scripts remain in:
- `setup/`
- `scripts/`
- `ai-product/`
- `axolotl/`

## Repo structure

- `v2/` multi-user platform app (current main path)
- `setup/` install and launch scripts
- `scripts/` chat and eval scripts
- `ai-product/` mode config and prompt policies
- `knowledge/` domain knowledge intake layout
- `eval/` prompt set and reports
- `axolotl/` fine-tune starter pipeline
