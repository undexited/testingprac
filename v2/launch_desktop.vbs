Option Explicit

Dim shell, fso, cmd, pyw1, pyw2, appPath
Set shell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

pyw1 = "C:\Users\helme\OneDrive\Documents\codexplay\.venv-openwebui\Scripts\pythonw.exe"
pyw2 = "C:\Users\helme\OneDrive\Documents\codexplay\.venv\Scripts\pythonw.exe"
appPath = "C:\Users\helme\OneDrive\Documents\codexplay\v2\desktop_app.py"

If fso.FileExists(pyw1) Then
    cmd = """" & pyw1 & """ """ & appPath & """"
ElseIf fso.FileExists(pyw2) Then
    cmd = """" & pyw2 & """ """ & appPath & """"
Else
    cmd = "pyw -3 """ & appPath & """"
End If

shell.Run cmd, 0, False
