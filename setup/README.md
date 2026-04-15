# Local AI Stack Setup

This workspace is prepared for:

- Ollama on Windows
- Open WebUI in a local Python virtual environment
- Axolotl in WSL/Ubuntu
- Optional automatic startup at Windows logon

## Files

- `setup/start-openwebui.ps1` starts Open WebUI from the local virtual environment
- `setup/start-ai-stack.ps1` starts Ollama and Open WebUI together
- `setup/setup-openwebui.ps1` creates the virtual environment and installs Open WebUI
- `setup/install-startup-task.ps1` installs a Windows scheduled task for auto-start
- `setup/setup-ollama-models.ps1` pulls a fast model and a thinking model
- `setup/setup-axolotl-wsl.sh` installs Axolotl inside WSL Ubuntu

## Expected local ports

- Ollama API: `11434`
- Open WebUI: `8080`

## Notes

Axolotl is Linux-first. On this Windows machine it should be installed inside WSL rather than natively.

## Recommended local model split

- Fast/default chat: `llama3.2:1b`
- Balanced chat: `llama3.2:3b`
- Thinking/deeper analysis: `qwen3:4b`
