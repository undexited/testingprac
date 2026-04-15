$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$openWebUiExe = Join-Path $root ".venv-openwebui\\Scripts\\open-webui.exe"
$dataDir = Join-Path $env:LOCALAPPDATA "open-webui-data"

if (-not (Test-Path $openWebUiExe)) {
    throw "Open WebUI virtual environment not found. Run setup\\setup-openwebui.ps1 first."
}

$null = New-Item -ItemType Directory -Force -Path $dataDir
$env:OLLAMA_BASE_URL = "http://127.0.0.1:11434"
$env:DATA_DIR = $dataDir
$env:PYTHONUTF8 = "1"
$env:PYTHONIOENCODING = "utf-8"
$env:LOG_FORMAT = "json"

& $openWebUiExe serve
