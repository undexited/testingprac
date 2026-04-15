$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$startStackScript = Join-Path $PSScriptRoot "start-ai-stack.ps1"
$appUrl = "http://127.0.0.1:8080"

function Wait-ForUrl {
    param(
        [string]$Url,
        [int]$TimeoutSeconds = 90
    )

    $start = Get-Date
    while (((Get-Date) - $start).TotalSeconds -lt $TimeoutSeconds) {
        try {
            $response = Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 5
            if ($response.StatusCode -ge 200 -and $response.StatusCode -lt 500) {
                return $true
            }
        }
        catch {
            Start-Sleep -Seconds 2
        }
    }

    return $false
}

# Ensure Ollama + Open WebUI are running.
& $startStackScript

$ready = Wait-ForUrl -Url $appUrl -TimeoutSeconds 90
if (-not $ready) {
    throw "Open WebUI did not become reachable at $appUrl within timeout."
}

$edgeCandidates = @(
    "$env:ProgramFiles(x86)\Microsoft\Edge\Application\msedge.exe",
    "$env:ProgramFiles\Microsoft\Edge\Application\msedge.exe"
)

$chromeCandidates = @(
    "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
    "$env:ProgramFiles(x86)\Google\Chrome\Application\chrome.exe"
)

$edge = $edgeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1
$chrome = $chromeCandidates | Where-Object { Test-Path $_ } | Select-Object -First 1

if ($edge) {
    Start-Process -FilePath $edge -ArgumentList "--app=$appUrl", "--new-window" -WorkingDirectory $root | Out-Null
}
elseif ($chrome) {
    Start-Process -FilePath $chrome -ArgumentList "--app=$appUrl", "--new-window" -WorkingDirectory $root | Out-Null
}
else {
    Start-Process $appUrl | Out-Null
}
