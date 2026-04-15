Option Explicit

Dim shell, command
Set shell = CreateObject("WScript.Shell")

command = "powershell.exe -NoProfile -ExecutionPolicy Bypass -File ""C:\Users\helme\OneDrive\Documents\codexplay\setup\launch-local-ai-app.ps1"""

' 0 = hidden window, False = do not wait
shell.Run command, 0, False
