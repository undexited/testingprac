#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

DO_UPDATE=0
DO_START=1
DO_WINDOWS=1
DO_AXOLOTL=1

log() {
  printf '[install] %s\n' "$*"
}

warn() {
  printf '[install][warn] %s\n' "$*" >&2
}

usage() {
  cat <<'EOF'
Usage: ./install.sh [options]

Options:
  --update         Pull latest committed repo changes before install
  --no-start       Do not start the AI stack at the end
  --skip-windows   Skip Windows/PowerShell setup steps
  --skip-axolotl   Skip Axolotl WSL/Linux setup step
  -h, --help       Show this help
EOF
}

to_host_path() {
  local p="$1"
  if command -v wslpath >/dev/null 2>&1; then
    wslpath -w "$p"
  elif command -v cygpath >/dev/null 2>&1; then
    cygpath -w "$p"
  else
    printf '%s' "$p"
  fi
}

run_ps_script() {
  local script_path="$1"
  local shell_cmd=""

  if command -v powershell.exe >/dev/null 2>&1; then
    shell_cmd="powershell.exe"
  elif command -v powershell >/dev/null 2>&1; then
    shell_cmd="powershell"
  else
    return 1
  fi

  local host_path
  host_path="$(to_host_path "$script_path")"
  log "Running PowerShell: ${script_path#$ROOT_DIR/}"
  "$shell_cmd" -NoProfile -ExecutionPolicy Bypass -File "$host_path"
}

run_windows_steps() {
  local ran_any=0
  local ps_files=()
  local post_files=()

  while IFS= read -r -d '' f; do ps_files+=("$f"); done < <(find "$ROOT_DIR/setup" -maxdepth 1 -type f -name 'setup-*.ps1' -print0 | sort -z)
  while IFS= read -r -d '' f; do post_files+=("$f"); done < <(find "$ROOT_DIR/setup" -maxdepth 1 -type f \( -name 'install-*.ps1' -o -name 'create-*.ps1' \) -print0 | sort -z)

  for f in "${ps_files[@]}"; do
    ran_any=1
    run_ps_script "$f"
  done

  for f in "${post_files[@]}"; do
    ran_any=1
    run_ps_script "$f"
  done

  if [[ "$DO_START" -eq 1 && -f "$ROOT_DIR/setup/start-ai-stack.ps1" ]]; then
    ran_any=1
    run_ps_script "$ROOT_DIR/setup/start-ai-stack.ps1"
  fi

  if [[ "$ran_any" -eq 0 ]]; then
    warn "No Windows setup scripts found in setup/."
  fi
}

run_axolotl_step() {
  local script="$ROOT_DIR/setup/setup-axolotl-wsl.sh"
  if [[ -f "$script" ]]; then
    log "Running Axolotl setup script."
    bash "$script"
  else
    warn "Axolotl setup script not found: $script"
  fi
}

for arg in "$@"; do
  case "$arg" in
    --update) DO_UPDATE=1 ;;
    --no-start) DO_START=0 ;;
    --skip-windows) DO_WINDOWS=0 ;;
    --skip-axolotl) DO_AXOLOTL=0 ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      warn "Unknown option: $arg"
      usage
      exit 1
      ;;
  esac
done

if [[ "$DO_UPDATE" -eq 1 ]]; then
  if [[ -d "$ROOT_DIR/.git" ]]; then
    log "Updating repository with git pull --ff-only."
    git -C "$ROOT_DIR" pull --ff-only
  else
    warn "No .git directory found; skipping update."
  fi
fi

if [[ "$DO_WINDOWS" -eq 1 ]]; then
  if command -v powershell.exe >/dev/null 2>&1 || command -v powershell >/dev/null 2>&1; then
    run_windows_steps
  else
    warn "PowerShell not found; skipping Windows setup steps."
  fi
fi

if [[ "$DO_AXOLOTL" -eq 1 ]]; then
  if [[ -f "$ROOT_DIR/setup/setup-axolotl-wsl.sh" ]]; then
    run_axolotl_step
  fi
fi

log "Install complete."
