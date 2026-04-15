# Local AI Product Playbook

This workspace now supports:

- Fast chat mode (`local-fast`)
- Thinking/deep-analysis mode (`local-think`)
- Repeatable evals with latency tracking
- Knowledge folder structure for Open WebUI uploads
- Axolotl fine-tuning starter pipeline

## Quick start

1. Start servers:
   - `powershell -ExecutionPolicy Bypass -File .\setup\start-ai-stack.ps1`
2. Open UI:
   - `http://127.0.0.1:8080`
3. Pull/create model aliases:
   - `powershell -ExecutionPolicy Bypass -File .\setup\setup-ollama-models.ps1`
4. Run local eval:
   - `powershell -ExecutionPolicy Bypass -File .\scripts\run-eval.ps1`

## Mode routing

- `fast`: low latency, short answers, default mode
- `think`: deeper reasoning, better for planning/analysis

Use the same prompt in both modes and compare via eval report before changing defaults.

## Behavior policy

Default policy file:

- `ai-product\prompts\system-default.md`

Deep-think policy file:

- `ai-product\prompts\system-think.md`

## Knowledge workflow

Put source documents in:

- `knowledge\inbox`

Then move curated docs into:

- `knowledge\business`
- `knowledge\coding`
- `knowledge\personal`

Upload curated folders to Open WebUI knowledge spaces by domain.

## Evals

- Prompt set: `eval\prompts.jsonl`
- Runner: `scripts\run-eval.ps1`
- Outputs: `eval\reports\`

Track latency and response quality weekly.

## Axolotl starter

- Dataset template: `axolotl\data\train.jsonl`
- Config template: `axolotl\configs\lora-qwen25-1_5b.yml`
- Runbook: `axolotl\README.md`
