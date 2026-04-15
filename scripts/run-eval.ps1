$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$promptPath = Join-Path $root "eval\\prompts.jsonl"
$reportDir = Join-Path $root "eval\\reports"

$null = New-Item -ItemType Directory -Force -Path $reportDir

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$csvPath = Join-Path $reportDir "eval-$timestamp.csv"
$jsonPath = Join-Path $reportDir "eval-$timestamp.json"

$rows = @()
$all = @()
$modes = @("fast", "think")

$prompts = Get-Content $promptPath | Where-Object { $_.Trim() -ne "" } | ForEach-Object { $_ | ConvertFrom-Json }

foreach ($p in $prompts) {
    foreach ($mode in $modes) {
        $start = Get-Date
        $output = powershell -ExecutionPolicy Bypass -File (Join-Path $root "scripts\\chat-local.ps1") -Mode $mode -Prompt $p.prompt
        $elapsedMs = [int]((Get-Date) - $start).TotalMilliseconds

        $row = [PSCustomObject]@{
            timestamp = $timestamp
            prompt_id = $p.id
            mode = $mode
            latency_ms = $elapsedMs
            chars = $output.Length
            output = $output
        }

        $rows += $row
        $all += $row
    }
}

$rows | Export-Csv -NoTypeInformation -Path $csvPath
$all | ConvertTo-Json -Depth 5 | Set-Content -Path $jsonPath

Write-Host "Eval complete."
Write-Host "CSV: $csvPath"
Write-Host "JSON: $jsonPath"
