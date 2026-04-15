param(
    [Parameter(Mandatory = $true)]
    [ValidateSet("fast", "think")]
    [string]$Mode,

    [Parameter(Mandatory = $true)]
    [string]$Prompt
)

$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
$modeConfigPath = Join-Path $root "ai-product\\modes.json"
$defaultSystem = (Get-Content (Join-Path $root "ai-product\\prompts\\system-default.md") -Raw).Trim()
$thinkSystem = (Get-Content (Join-Path $root "ai-product\\prompts\\system-think.md") -Raw).Trim()

$config = Get-Content $modeConfigPath -Raw | ConvertFrom-Json
$selected = $config.$Mode

$systemPrompt = if ($Mode -eq "think") { $thinkSystem } else { $defaultSystem }

$body = @{
    model = $selected.model
    system = $systemPrompt
    prompt = $Prompt
    stream = $false
    options = @{
        temperature = [double]$selected.temperature
        num_predict = [int]$selected.num_predict
    }
} | ConvertTo-Json -Depth 6

$response = Invoke-RestMethod -Uri "http://127.0.0.1:11434/api/generate" -Method Post -ContentType "application/json" -Body $body
$response.response
