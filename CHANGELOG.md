# Changelog

All notable changes to this project are documented in this file.

## [v2.0.1] - 2026-04-16

### Added
- Added desktop app mode in `v2/desktop_app.py` with:
  - Chat + agent selection
  - Code Studio with open/save file workflow and snippet execution
  - Admin login event feed view
- Added hidden desktop launcher `v2/launch_desktop.vbs` and shortcut helper `setup/create-v2-desktop-shortcut.ps1`.
- Added `v2/smoke_test.py` for end-to-end local verification of auth/workspaces/admin/agents/chat.

### Changed
- Updated provider gateway defaults to prioritize hosted providers with local fallback:
  - default order `openai,anthropic,builtin`
  - new `builtin` provider for no-external-backend operation
- Added SQLite compatibility upgrade handling in `v2/app/db.py` to avoid runtime errors when older local DB schema exists.
- Updated docs and env defaults for desktop-first usage and provider routing.

## [v2.0.0] - 2026-04-15

### Added
- Added a new production-oriented app scaffold in `v2/` that replaces the Open WebUI concept for primary product direction.
- Added multi-user backend with FastAPI:
  - registration/login with JWT auth
  - per-user conversations and messages
  - chat endpoint with persistence
- Added provider gateway abstraction in `v2/app/gateway.py`:
  - `ollama`
  - `openai` (configurable)
  - `anthropic` (configurable)
- Added mode-aware routing (`fast` and `think`) with configurable model mapping.
- Added new ChatGPT-style first-party frontend in `v2/web/`.
- Added `v2/.env.example`, `v2/requirements.txt`, `v2/run.ps1`, and `v2/README.md`.

## [v0.1.1] - 2026-04-15

### Added
- Added hidden launcher script: `setup/launch-local-ai-app.vbs`.

### Changed
- Updated desktop shortcut creation script to launch via `wscript.exe` instead of direct `powershell.exe`.
- Desktop app launch now avoids opening visible PowerShell/CMD windows.

## [v0.1.0] - 2026-04-15

### Added
- Initial local AI app stack with Open WebUI + Ollama startup scripts.
- Fast/think local model routing and chat scripts.
- Evaluation harness with CSV/JSON report generation.
- Axolotl starter training pipeline and templates.
- Unified installer (`install.sh`) and CI workflow.
