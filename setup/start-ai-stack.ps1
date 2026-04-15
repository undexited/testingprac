$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$ollamaExe = "C:\Users\helme\AppData\Local\Programs\Ollama\ollama app.exe"
$openWebUiStartScript = Join-Path $PSScriptRoot "start-openwebui.ps1"

function Test-PortListening {
    param([int]$Port)

    return [bool](Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue |
        Where-Object { $_.LocalPort -eq $Port } |
        Select-Object -First 1)
}

if (-not (Test-PortListening -Port 11434)) {
    if (-not (Test-Path $ollamaExe)) {
        throw "Ollama app executable not found at $ollamaExe"
    }

    Start-Process -FilePath $ollamaExe | Out-Null
    Start-Sleep -Seconds 8
}

if (-not (Test-PortListening -Port 8080)) {
    Start-Process -FilePath "powershell.exe" `
        -ArgumentList "-NoProfile", "-WindowStyle", "Hidden", "-ExecutionPolicy", "Bypass", "-File", $openWebUiStartScript `
        -WorkingDirectory $root | Out-Null
}
