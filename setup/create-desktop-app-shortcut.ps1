$ErrorActionPreference = "Stop"

$launcherVbs = "C:\Users\helme\OneDrive\Documents\codexplay\setup\launch-local-ai-app.vbs"
if (-not (Test-Path $launcherVbs)) {
    throw "Launcher not found: $launcherVbs"
}

$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "Local AI App.lnk"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "wscript.exe"
$shortcut.Arguments = "`"$launcherVbs`""
$shortcut.WorkingDirectory = "C:\Users\helme\OneDrive\Documents\codexplay"
$shortcut.IconLocation = "C:\Users\helme\AppData\Local\Programs\Ollama\ollama app.exe,0"
$shortcut.Save()

Write-Host "Created desktop shortcut: $shortcutPath"
