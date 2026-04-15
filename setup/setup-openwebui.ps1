$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$preferredPython = "C:\Users\helme\AppData\Local\Programs\Python\Python311\python.exe"

if (Test-Path $preferredPython) {
    $pythonExe = $preferredPython
} else {
    $pythonExe = "python"
}

Push-Location $root
try {
    & $pythonExe -m venv .venv-openwebui

    $venvPython = Join-Path $root ".venv-openwebui\\Scripts\\python.exe"
    & $venvPython -m pip install --upgrade pip
    & $venvPython -m pip install open-webui

    Write-Host ""
    Write-Host "Open WebUI installed."
    Write-Host "Start it with: powershell -ExecutionPolicy Bypass -File .\\setup\\start-openwebui.ps1"
}
finally {
    Pop-Location
}
