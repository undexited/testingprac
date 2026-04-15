#!/usr/bin/env bash
set -euo pipefail

sudo apt-get update
sudo apt-get install -y python3 python3-venv python3-pip git build-essential

mkdir -p "$HOME/axolotl"
cd "$HOME/axolotl"

python3 -m venv .venv
source .venv/bin/activate

python -m pip install --upgrade pip
python -m pip install axolotl

echo
echo "Axolotl installed in \$HOME/axolotl/.venv"
echo "Activate with: source \$HOME/axolotl/.venv/bin/activate"
