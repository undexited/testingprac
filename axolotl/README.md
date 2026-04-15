# Axolotl Fine-Tune Starter

This starter is designed for WSL Ubuntu where `axolotl` is already installed.

## Files

- `axolotl\data\train.jsonl` - starter supervised fine-tune dataset
- `axolotl\configs\lora-qwen25-1_5b.yml` - LoRA config template

## Run in WSL

From Ubuntu shell:

```bash
cd /mnt/c/Users/helme/OneDrive/Documents/codexplay
source ~/axolotl/.venv/bin/activate
axolotl train axolotl/configs/lora-qwen25-1_5b.yml
```

## Export notes

After training, merge/export adapter and test in Ollama by creating a model package from merged weights.
