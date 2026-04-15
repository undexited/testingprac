$ErrorActionPreference = "Stop"

$launcher = "C:\Users\helme\OneDrive\Documents\codexplay\setup\launch-local-ai-app.ps1"
if (-not (Test-Path $launcher)) {
    throw "Launcher not found: $launcher"
}

$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "Local AI App.lnk"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "powershell.exe"
$shortcut.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$launcher`""
$shortcut.WorkingDirectory = "C:\Users\helme\OneDrive\Documents\codexplay"
$shortcut.IconLocation = "C:\Users\helme\AppData\Local\Programs\Ollama\ollama app.exe,0"
$shortcut.Save()

Write-Host "Created desktop shortcut: $shortcutPath"
