# Local AI App Stack (`testingprac`)

This repo packages a full local AI system you can run as a desktop app on your computer:

- `Ollama` local inference backend
- `Open WebUI` local chat UI (`http://127.0.0.1:8080`)
- Fast + thinking model modes (`local-fast`, `local-think`)
- Evaluation harness with latency reporting
- Knowledge folder workflow
- Axolotl fine-tuning starter in WSL

## What you get

- One-click app launcher and desktop shortcut
- Startup automation at logon (Scheduled Task or HKCU Run fallback)
- Idempotent setup scripts in `setup/`
- Single root installer (`install.sh`) to run everything

## Quick install

From repo root:

```bash
chmod +x install.sh
./install.sh
```

This runs:

1. Windows setup scripts (`setup/setup-*.ps1`)
2. Startup/shortcut scripts (`setup/install-*.ps1`, `setup/create-*.ps1`)
3. WSL Axolotl setup (`setup/setup-axolotl-wsl.sh`) when running in Linux/WSL
4. Starts the stack unless disabled

## Keep setup synced with future updates

Use:

```bash
./install.sh --update
```

`--update` performs a `git pull --ff-only` first, then executes current setup scripts from this repo.
That means your installer always reflects the latest committed setup changes.

## Useful flags

```bash
./install.sh --no-start
./install.sh --skip-windows
./install.sh --skip-axolotl
./install.sh --update
```

## Run as desktop app

- Desktop shortcut: `Local AI App.lnk`
- Or run:

```powershell
powershell -ExecutionPolicy Bypass -File .\setup\launch-local-ai-app.ps1
```

## Model modes

- `local-fast`: speed/low latency
- `local-think`: deeper analysis

Test mode calls:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\chat-local.ps1 -Mode fast -Prompt "Hello"
powershell -ExecutionPolicy Bypass -File .\scripts\chat-local.ps1 -Mode think -Prompt "Analyze tradeoffs for X"
```

## Evaluation

Run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run-eval.ps1
```

Outputs are written to `eval/reports/` as CSV + JSON.

## Fine-tuning (Axolotl)

In WSL:

```bash
source ~/axolotl/.venv/bin/activate
axolotl train axolotl/configs/lora-qwen25-1_5b.yml
```

Starter files:

- `axolotl/data/train.jsonl`
- `axolotl/configs/lora-qwen25-1_5b.yml`

## Repo structure

- `setup/` install and launch scripts
- `scripts/` chat and eval scripts
- `ai-product/` mode config and prompt policies
- `knowledge/` domain knowledge intake layout
- `eval/` prompt set and reports
- `axolotl/` fine-tune starter pipeline
