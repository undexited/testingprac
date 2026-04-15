# Changelog

All notable changes to this project are documented in this file.

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
