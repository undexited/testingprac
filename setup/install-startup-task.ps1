$ErrorActionPreference = "Stop"

$taskName = "Local AI Stack"
$launcher = "C:\Users\helme\OneDrive\Documents\codexplay\setup\start-ai-stack.ps1"
$runKey = "HKCU:\Software\Microsoft\Windows\CurrentVersion\Run"
$runName = "LocalAIStack"
$runValue = "powershell.exe -NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$launcher`""

if (-not (Test-Path $launcher)) {
    throw "Launcher script not found at $launcher"
}

try {
    $action = New-ScheduledTaskAction `
        -Execute "powershell.exe" `
        -Argument "-NoProfile -WindowStyle Hidden -ExecutionPolicy Bypass -File `"$launcher`""

    $trigger = New-ScheduledTaskTrigger -AtLogOn
    $settings = New-ScheduledTaskSettingsSet `
        -AllowStartIfOnBatteries `
        -DontStopIfGoingOnBatteries `
        -MultipleInstances IgnoreNew `
        -StartWhenAvailable

    Register-ScheduledTask `
        -TaskName $taskName `
        -Action $action `
        -Trigger $trigger `
        -Settings $settings `
        -Description "Starts Ollama and Open WebUI at Windows logon." `
        -Force | Out-Null

    Write-Host "Scheduled task '$taskName' installed."
}
catch {
    Set-ItemProperty -Path $runKey -Name $runName -Value $runValue -Type String
    Write-Host "Scheduled task install failed; set HKCU Run fallback '$runName' instead."
}
