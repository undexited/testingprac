$ErrorActionPreference = "Stop"

$root = $PSScriptRoot
$pythonExe = "C:\Users\helme\OneDrive\Documents\codexplay\.venv-openwebui\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    $pythonExe = "C:\Users\helme\AppData\Local\Programs\Python\Python311\python.exe"
}

if (-not (Test-Path $pythonExe)) {
    $pythonExe = "python"
}

Push-Location $root
try {
    if (-not (Test-Path ".env")) {
        Copy-Item ".env.example" ".env"
    }

    $dbDir = Join-Path $env:LOCALAPPDATA "testingprac-ai-v2"
    $null = New-Item -ItemType Directory -Force -Path $dbDir
    $dbPath = (Join-Path $dbDir "app.db") -replace "\\", "/"
    $env:DATABASE_URL = "sqlite:///$dbPath"

    & $pythonExe -m uvicorn app.main:app --host 127.0.0.1 --port 8090 --reload
}
finally {
    Pop-Location
}
