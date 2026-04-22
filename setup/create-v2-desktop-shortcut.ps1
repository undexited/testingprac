$ErrorActionPreference = "Stop"

$launcherVbs = "C:\Users\helme\OneDrive\Documents\codexplay\v2\launch_desktop.vbs"
if (-not (Test-Path $launcherVbs)) {
    throw "Launcher not found: $launcherVbs"
}

$desktopPath = [Environment]::GetFolderPath("Desktop")
$shortcutPath = Join-Path $desktopPath "TestingPrac AI v2 Desktop.lnk"

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($shortcutPath)
$shortcut.TargetPath = "wscript.exe"
$shortcut.Arguments = "`"$launcherVbs`""
$shortcut.WorkingDirectory = "C:\Users\helme\OneDrive\Documents\codexplay\v2"
$shortcut.IconLocation = "C:\Windows\System32\shell32.dll,220"
$shortcut.Save()

Write-Host "Created desktop shortcut: $shortcutPath"
