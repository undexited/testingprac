$ErrorActionPreference = "Stop"

$ollamaExe = "C:\Users\helme\AppData\Local\Programs\Ollama\ollama.exe"
$root = Split-Path -Parent $PSScriptRoot
$models = @(
    "llama3.2:1b",
    "qwen3:4b"
)

foreach ($model in $models) {
    & $ollamaExe pull $model
}

& $ollamaExe create local-fast -f (Join-Path $root "setup\\models\\local-fast.Modelfile")
& $ollamaExe create local-think -f (Join-Path $root "setup\\models\\local-think.Modelfile")

Write-Host "Done. Available aliases: local-fast, local-think"
